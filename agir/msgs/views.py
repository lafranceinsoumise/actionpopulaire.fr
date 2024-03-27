from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from agir.groups.models import Membership, SupportGroup
from agir.lib.pagination import APIPageNumberPagination
from agir.msgs.actions import (
    get_unread_message_count,
    read_all_user_messages,
    get_user_messages_count,
)
from agir.msgs.models import (
    SupportGroupMessage,
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
        read_all_user_messages(person)

        return Response(True)


class UserMessagesAPIView(ListAPIView):
    serializer_class = UserMessagesSerializer
    permission_classes = (IsPersonPermission,)
    pagination_class = None

    def list(self, request, *args, **kwargs):
        paginator = APIPageNumberPagination()

        page_size = paginator.get_page_size(self.request)
        total_messages = get_user_messages_count(self.request.user.person)

        # la valeur par défaut est pour le cas sans message
        max_page = (total_messages - 1) // page_size + 1 or 1

        page_number = self.request.query_params.get(paginator.page_query_param, 1)
        if page_number in paginator.last_page_strings:
            page_number = max_page

        try:
            page_number = int(page_number)
        except (TypeError, ValueError):
            raise NotFound("Page incorrecte")

        if not (1 <= page_number <= max_page):
            raise NotFound("Page incorrecte")

        person = self.request.user.person
        messages = get_user_messages(
            person, (page_number - 1) * page_size, page_number * page_size
        )
        serializer = self.get_serializer(messages, many=True)

        url = self.request.build_absolute_uri()
        next_url = (
            None
            if page_number == max_page
            else replace_query_param(url, paginator.page_query_param, page_number + 1)
        )
        prev_url = (
            None
            if page_number == 1
            else replace_query_param(url, paginator.page_query_param, page_number - 1)
        )

        return Response(
            {
                "count": total_messages,
                "next": next_url,
                "previous": prev_url,
                "results": serializer.data,
            }
        )


@api_view(["GET"])
@permission_classes((IsPersonPermission,))
def unread_message_count(request):
    return Response(
        {"unreadMessageCount": get_unread_message_count(request.user.person)}
    )
