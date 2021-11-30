from django.db.models import (
    Case,
    DateTimeField,
    Exists,
    IntegerField,
    Max,
    OuterRef,
    When,
    Prefetch,
    Count,
    Subquery,
    Q,
)
from django.db.models.functions import Greatest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.groups.models import Membership, SupportGroup
from agir.msgs.actions import get_unread_message_count
from agir.msgs.models import (
    SupportGroupMessage,
    SupportGroupMessageRecipient,
    SupportGroupMessageComment,
)
from agir.msgs.serializers import (
    UserReportSerializer,
    UserMessagesSerializer,
    UserMessageRecipientSerializer,
)
from itertools import chain
from operator import attrgetter


class UserReportAPIView(CreateAPIView):
    serializer_class = UserReportSerializer
    permission_classes = (IsAuthenticated,)


class UserMessageRecipientsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserMessageRecipientSerializer
    queryset = SupportGroup.objects.active()

    def get_queryset(self):
        person = self.request.user.person
        return (
            self.queryset.filter(
                memberships__person=person,
                memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
            )
            .values("id", "name")
            .order_by("name")
        )


class UserMessagesAPIView(ListAPIView):
    serializer_class = UserMessagesSerializer
    queryset = SupportGroupMessage.objects.exclude(deleted=True)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        person = self.request.user.person
        person_groups = (
            SupportGroup.objects.active()
            .filter(memberships__person=person)
            .values("id")
        )

        user_message = SupportGroupMessageRecipient.objects.filter(
            recipient=person, message_id=OuterRef("id")
        )

        # For private messages: get groups where person is referent
        person_referent_groups = (
            SupportGroup.objects.filter(
                id__in=person_groups,
                memberships__person=person,
                memberships__membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
            )
            .values("id")
            .distinct()
        )

        # Private messages from type organization = is_author + is allowed in group messages
        private_group_messages = list(
            SupportGroupMessage.objects.filter(
                author=person,
                message_type=SupportGroupMessage.MESSAGE_TYPE_ORGANIZATION,
            ).annotate(
                last_update=Greatest(
                    Max("comments__created"), "created", output_field=DateTimeField()
                )
            )
        ) + list(
            SupportGroupMessage.objects.filter(
                supportgroup__in=person_referent_groups,
                message_type=SupportGroupMessage.MESSAGE_TYPE_ORGANIZATION,
            )
            .exclude(author=person)
            .annotate(
                last_update=Greatest(
                    Max("comments__created"), "created", output_field=DateTimeField()
                )
            )
        )

        public_group_messages = (
            self.queryset.filter(
                supportgroup_id__in=person_groups,
                message_type=SupportGroupMessage.MESSAGE_TYPE_DEFAULT,
            )
            .select_related("supportgroup", "author")
            .prefetch_related("comments")
            .annotate(
                is_unread=Case(
                    When(
                        created__lt=Subquery(
                            Membership.objects.filter(
                                supportgroup_id=OuterRef("supportgroup_id"),
                                person_id=person.pk,
                            ).values("created")[:1]
                        ),
                        then=False,
                    ),
                    default=~Exists(user_message),
                )
            )
            .annotate(
                last_update=Greatest(
                    Max("comments__created"), "created", output_field=DateTimeField()
                )
            )
            .distinct()
        )

        return sorted(
            chain(private_group_messages, public_group_messages),
            key=attrgetter("created", "last_update"),
            reverse=True,
        )


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def unread_message_count(request):
    return Response(
        {"unreadMessageCount": get_unread_message_count(request.user.person)}
    )
