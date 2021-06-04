from django.db.models import (
    Case,
    DateTimeField,
    Exists,
    IntegerField,
    Max,
    OuterRef,
    When,
)
from django.db.models.functions import Greatest
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from agir.groups.models import Membership, SupportGroup
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageRecipient
from agir.msgs.serializers import (
    UserReportSerializer,
    UserMessagesSerializer,
    UserMessageRecipientSerializer,
)


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

        return (
            self.queryset.filter(supportgroup_id__in=person_groups)
            .select_related("supportgroup", "author")
            .prefetch_related("comments")
            .annotate(is_unread=~Exists(user_message))
            .annotate(
                last_comment=Greatest(
                    Max("comments__created"), "created", output_field=DateTimeField()
                )
            )
            .distinct()
            .order_by("-last_comment", "-created")
        )
