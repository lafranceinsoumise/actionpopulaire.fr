from django.utils.functional import cached_property
from glom import glom, T, Call

from agir.authentication.models import Role
from agir.notifications.models import Notification


def get_notifications(request):
    if request.user.is_anonymous or request.user.type == Role.CLIENT_ROLE:
        return []

    person = request.user.person

    statuses = {
        ns["notification_id"]: ns["status"]
        for ns in person.notification_statuses.all().values("notification_id", "status")
    }

    spec = [
        {
            "id": "id",
            "content": "content",
            "link": "link",
            "status": Call(statuses.get, args=(T.id, "U")),
        }
    ]

    instances = [
        n
        for n in Notification.objects.active().select_related("segment")
        if not n.segment
        or n.segment.get_subscribers_queryset.filter(pk=person.pk).exists()
    ]

    return glom(instances, spec)


class NotificationRequestManager:
    def __init__(self, request):
        self.request = request

    @cached_property
    def _notifications(self):
        return get_notifications(self.request)

    def __iter__(self):
        return iter(self._notifications)

    def unread(self):
        return sum(not n.seen for n in self._notifications)
