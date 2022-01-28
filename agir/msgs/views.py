from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
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
from agir.lib.pagination import APIPaginator
from agir.msgs.tasks import send_message_report_email
from .utils import get_user_messages


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


# Mark all message read
class UserMessagesAllReadAPIView(RetrieveAPIView):
    queryset = SupportGroupMessage.objects.all()
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        person = self.request.user.person
        messages = get_user_messages(person)

        for message in messages:
            SupportGroupMessageRecipient.objects.update_or_create(
                message=message,
                recipient=person,
            )
        return Response(True)


class UserMessagesAPIView(ListAPIView):
    serializer_class = UserMessagesSerializer
    queryset = SupportGroupMessage.objects.exclude(deleted=True)
    permission_classes = (IsAuthenticated,)
    pagination_class = APIPaginator

    def get_queryset(self):
        person = self.request.user.person
        return get_user_messages(person)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def unread_message_count(request):
    return Response(
        {"unreadMessageCount": get_unread_message_count(request.user.person)}
    )
