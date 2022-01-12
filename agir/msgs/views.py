from django.db.models import (
    Case,
    DateTimeField,
    Exists,
    Max,
    OuterRef,
    When,
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
)
from agir.msgs.serializers import (
    UserReportSerializer,
    UserMessagesSerializer,
    UserMessageRecipientSerializer,
)
from agir.msgs.tasks import send_message_report_email


class UserReportAPIView(CreateAPIView):
    serializer_class = UserReportSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        super(UserReportAPIView, self).perform_create(serializer)
        send_message_report_email.delay(serializer.instance.pk)


class UserMessageRecipientsView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserMessageRecipientSerializer
    queryset = SupportGroup.objects.active()

    def get_queryset(self):
        person = self.request.user.person
        return (
            self.queryset.filter(
                memberships__person=person,
                memberships__person__role__is_active=True,
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

        # Get messages where person is author or is in group
        group_messages = (
            self.queryset.filter(
                (Q(supportgroup_id__in=person_groups) | Q(author=person))
                & Q(author__role__is_active=True)
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
            .order_by("-last_update", "-created")
        )

        # Filter messages where person is not in allowed membership types
        return [
            msg
            for msg in group_messages
            if person.role.has_perm("msgs.view_supportgroupmessage", msg)
        ]


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def unread_message_count(request):
    return Response(
        {"unreadMessageCount": get_unread_message_count(request.user.person)}
    )
