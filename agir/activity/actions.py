from django.db.models import Prefetch, Q
from django.utils import timezone

from .models import Activity, Announcement
from .serializers import ActivitySerializer, AnnouncementSerializer
from ..events.models import Event


def get_activity(person):
    return (
        Activity.objects.filter(recipient=person)
        .exclude(status=Activity.STATUS_INTERACTED)
        .prefetch_related(
            Prefetch("event", Event.objects.with_serializer_prefetch(person),)
        )
    )


def get_serialized_activity(request):
    if hasattr(request.user, "person"):
        person = request.user.person
        activities = get_activity(person)

        activity_serializer = ActivitySerializer(
            instance=activities, many=True, context={"request": request}
        )
        return activity_serializer.data

    return []


def get_announcements(person=None):
    today = timezone.now()
    cond = Q(start_date__lt=today) & (Q(end_date__isnull=True) | Q(end_date__gt=today))

    announcements = Announcement.objects.filter(cond).select_related("segment")

    if person:
        return [
            a
            for a in announcements
            if a.segment is None
            or a.segment.get_subscribers_queryset().filter(pk=person.id).exists()
        ]
    else:
        return announcements.filter(segment__isnull=True)


def get_serialized_announcements(request):
    person = getattr(request.user, "person", None)
    announcements = get_announcements(person)

    serializer = AnnouncementSerializer(
        instance=announcements, many=True, context={"request": request}
    )
    return serializer.data
