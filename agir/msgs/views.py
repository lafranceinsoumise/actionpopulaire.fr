from django.db import transaction
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response

from agir.groups.models import Membership, SupportGroup
from agir.lib.pagination import APIPageNumberPagination
from agir.msgs.actions import get_unread_message_count, get_viewable_messages_ids
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
from .actions import get_user_messages
from ..lib.rest_framework_permissions import IsPersonPermission


class UserReportAPIView(CreateAPIView):
    serializer_class = UserReportSerializer
    permission_classes = (IsPersonPermission,)

    def perform_create(self, serializer):
        super(UserReportAPIView, self).perform_create(serializer)
        send_message_report_email.delay(serializer.instance.pk)


class UserMessageRecipientsView(ListAPIView):
    permission_classes = (IsPersonPermission,)
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


# Mark all message read
class UserMessagesAllReadAPIView(RetrieveAPIView):
    queryset = SupportGroupMessage.objects.all()
    permission_classes = (IsPersonPermission,)

    def get(self, request, *args, **kwargs):
        person = self.request.user.person
        person_message_ids = get_viewable_messages_ids(person)
        with transaction.atomic():
            old_message_ids = SupportGroupMessageRecipient.objects.filter(
                message_id__in=person_message_ids, recipient=person
            ).values_list("message_id", flat=True)
            SupportGroupMessageRecipient.objects.bulk_create(
                (
                    SupportGroupMessageRecipient(
                        message_id=message_id, recipient=person
                    )
                    for message_id in person_message_ids
                    if message_id not in old_message_ids
                ),
                ignore_conflicts=True,
            )

            SupportGroupMessageRecipient.objects.filter(
                message_id__in=old_message_ids, recipient=person
            ).update(modified=timezone.now())

            return Response(True)


class UserMessagesAPIView(ListAPIView):
    serializer_class = UserMessagesSerializer
    queryset = SupportGroupMessage.objects.active()
    permission_classes = (IsPersonPermission,)
    pagination_class = APIPageNumberPagination

    def get_queryset(self):
        person = self.request.user.person
        return get_user_messages(person)


@api_view(["GET"])
@permission_classes((IsPersonPermission,))
def unread_message_count(request):
    return Response(
        {"unreadMessageCount": get_unread_message_count(request.user.person)}
    )
