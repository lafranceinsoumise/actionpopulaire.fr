from django.db import IntegrityError
from django.db.models import Exists, OuterRef
from django.utils.functional import cached_property
from glom import glom, T, Coalesce

from agir.authentication.models import Role
from agir.notifications.models import Announcement, Notification


def add_announcements(person):
    announcements = (
        Announcement.objects.active()
        .annotate(
            already_added=Exists(
                Notification.objects.filter(
                    person=person, announcement_id=OuterRef("id")
                )
            )
        )
        .exclude(already_added=True)
        .select_related("segment")
    )

    for gn in announcements:
        if (
            not gn.segment
            or gn.segment.get_subscribers_queryset().filter(id=person.pk).exists()
        ):
            try:
                Notification.objects.create(
                    person=person, announcement=gn, created=gn.start_date
                )
            except IntegrityError:
                pass


def get_notifications(request):
    if request.user.is_anonymous or request.user.type == Role.CLIENT_ROLE:
        return []

    person = request.user.person
    add_announcements(person)

    notifications = person.notifications.all().select_related("announcement")[:5]

    return serialize_notifications(notifications)


def serialize_notifications(notifications):
    # All fields are either
    spec = [
        {
            "id": "id",
            "status": "status",
            "content": Coalesce("content", "announcement.content", skip="", default=""),
            "icon": Coalesce("icon", "announcement.icon", skip="", default=""),
            "link": Coalesce("link", "announcement.link", skip="", default=""),
            "created": (Coalesce("announcement.start_date", "created"), T.isoformat()),
        }
    ]

    return glom(notifications, spec)


class NotificationRequestManager:
    def __init__(self, request):
        self.request = request

    @cached_property
    def notifications(self):
        return get_notifications(self.request)

    def __iter__(self):
        return iter(self.notifications)

    def unread(self):
        return sum(not n.seen for n in self.notifications)


def add_notification(**kwargs):
    Notification.objects.create(**kwargs)
