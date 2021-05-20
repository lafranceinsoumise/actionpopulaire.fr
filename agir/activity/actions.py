from django.db.models import Prefetch, Q, Subquery, OuterRef
from django.utils import timezone

from .models import Activity, Announcement
from .serializers import ActivitySerializer, AnnouncementSerializer
from ..events.models import Event


def get_activities(person):
    return (
        activity
        for activity in Activity.objects.without_required_action()
        .filter(recipient=person)
        .select_related("supportgroup", "individual")
        .prefetch_related(
            Prefetch(
                "event",
                Event.objects.with_serializer_prefetch(person).select_related(
                    "subtype"
                ),
            )
        )[:40]
        if person.role.has_perm("activity.view_activity", activity)
    )


def get_required_action_activities(person):
    required_action_activities = (
        Activity.objects.with_required_action()
        .filter(recipient=person)
        .select_related("supportgroup", "individual")
        .prefetch_related(
            Prefetch("event", Event.objects.with_serializer_prefetch(person),)
        )
    )
    # On affiche toutes les activités avec action requise non traitées
    unread_required_action_activities = required_action_activities.exclude(
        status=Activity.STATUS_INTERACTED
    )
    # On affiche les 20 dernières activités avec action requise déjà traitées
    read_required_action_activities = required_action_activities.filter(
        status=Activity.STATUS_INTERACTED
    ).order_by("-created")[:20]

    return (
        activity
        for activity in required_action_activities.filter(
            pk__in=[a.pk for a in unread_required_action_activities]
            + [a.pk for a in read_required_action_activities]
        ).order_by("-created")
        if person.role.has_perm("activity.view_activity", activity)
    )


def get_announcements(person=None):
    today = timezone.now()
    cond = Q(start_date__lt=today) & (Q(end_date__isnull=True) | Q(end_date__gt=today))

    # Les annonces sont affichés :
    # - avec les plus grandes priorités d'abord
    # - à priorité égale, les plus récentes d'abord
    # - à priorité et date de début égales, celles qui disparaitront les premières d'abord
    announcements = Announcement.objects.filter(cond).order_by(
        "-priority", "-start_date", "end_date"
    )

    if person:
        return [
            a
            for a in announcements.exclude(
                Q(
                    activity__in=Activity.objects.filter(
                        recipient=person, status=Activity.STATUS_INTERACTED
                    )
                ),
                ~Q(custom_display=""),
            )
            .annotate(
                activity_id=Subquery(
                    Activity.objects.filter(
                        recipient=person, announcement_id=OuterRef("id")
                    ).values("id")[:1]
                )
            )
            .select_related("segment")
            if a.segment is None
            or a.segment.get_subscribers_queryset().filter(pk=person.id).exists()
        ]
    else:
        return announcements.filter(segment__isnull=True)
