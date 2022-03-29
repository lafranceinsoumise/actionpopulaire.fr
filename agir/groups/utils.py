from datetime import timedelta

from django.db.models import Q
from django.utils.timezone import now

from ..events.models import Event, GroupAttendee


def is_active_group_filter():
    n = now()
    return Q(
        organized_events__start_time__range=(
            n - timedelta(days=62),
            n + timedelta(days=31),
        ),
        organized_events__visibility=Event.VISIBILITY_PUBLIC,
    ) | Q(created__gt=n - timedelta(days=31))


# Get events of group + events where group is attendee
def get_events_with_group(queryset, supportgroup):
    return queryset.filter(
        Q(organizers_groups__in=[supportgroup]) | Q(groups_attendees__in=[supportgroup])
    )
