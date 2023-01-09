from datetime import timedelta

from django.db.models import Q, Max, DateField
from django.utils.timezone import now

from agir.groups.models import SupportGroup
from agir.events.models import Event

DAYS_SINCE_GROUP_CREATION_LIMIT = 31
DAYS_SINCE_LAST_EVENT_LIMIT = 62
DAYS_SINCE_LAST_EVENT_WARNING = 45


def is_new_group_filter():
    # âge du groupe = maintenant - date de création <= durée max
    # ==>
    # date de création > maintenant - durée max
    limit_group_creation_date = now() - timedelta(days=DAYS_SINCE_GROUP_CREATION_LIMIT)
    return Q(created__gte=limit_group_creation_date)


def has_recent_event_filter():
    # âge de l'événement = maintenant - date événement <= durée max
    # =>
    # date événement >= maintenant - durée max
    limit_event_date = now() - timedelta(days=DAYS_SINCE_LAST_EVENT_LIMIT)
    return Q(
        organized_events__start_time__gte=limit_event_date,
        organized_events__visibility=Event.VISIBILITY_PUBLIC,
    )


def is_active_group_filter():
    return is_new_group_filter() | has_recent_event_filter()


def get_soon_to_be_inactive_groups(exact=False):
    # âge dernier événement = maintenant - date événement =/<= durée d'avertissement
    # ==>
    # date événement =/>= maintenant - durée d'avertissement = date limite
    limit_date = (now() - timedelta(days=DAYS_SINCE_LAST_EVENT_WARNING)).date()
    qs = (
        SupportGroup.objects.active()
        .exclude(is_new_group_filter())
        .annotate(
            last_event_start_date=Max(
                "organized_events__start_time__date",
                filter=Q(organized_events__visibility=Event.VISIBILITY_PUBLIC),
                output_field=DateField(),
            )
        )
    )
    if exact:
        # Keep only groups :
        # - with no events whose creation date was exactly n days ago
        # - whose last event start date was n days ago
        return qs.filter(
            Q(last_event_start_date__isnull=True, created__date=limit_date)
            | Q(last_event_start_date=limit_date)
        )

    # Keep only groups :
    # - with recent events, but whose last event start date was n days ago or more
    return qs.filter(has_recent_event_filter()).filter(
        Q(last_event_start_date__lte=limit_date)
    )
