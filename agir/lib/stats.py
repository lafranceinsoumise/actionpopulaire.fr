from datetime import timedelta

from django.conf import settings
from django.db.models import Count

from agir.people.models import Person
from agir.groups.models import SupportGroup, Membership
from agir.events.models import Event, EventSubtype


def get_general_stats(start, end):
    week = timedelta(days=7)
    nouveaux_soutiens = Person.objects.filter(
        meta__subscriptions__NSP__date__gt=start.isoformat(),
        meta__subscriptions__NSP__date__lt=end.isoformat(),
    )

    membres_equipes = Person.objects.filter(
        memberships__supportgroup__type=SupportGroup.TYPE_2022,
        memberships__supportgroup__published=True,
    )

    return {
        "Nouveaux soutiens NSP (total)": nouveaux_soutiens.count(),
        "Nouveaux soutiens NSP (insoumis)": nouveaux_soutiens.filter(
            is_insoumise=True
        ).count(),
        "Utilisateurs d'actionpopulaire.fr": Person.objects.filter(
            role__last_login__range=(start, end)
        ).count(),
        "Événements ayant eu lieu": Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC, start_time__range=(start, end)
        ).count(),
        "Nouveaux groupes d'actions": SupportGroup.objects.active()
        .filter(type=SupportGroup.TYPE_LOCAL_GROUP, created__range=(start, end))
        .count(),
        "Nouveaux membres de groupes d'actions": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True,
        )
        .filter(memberships__created__range=(start, end))
        .distinct()
        .count(),
        "Nouvelles équipes de soutiens": SupportGroup.objects.active()
        .filter(type=SupportGroup.TYPE_2022, created__range=(start, end))
        .count(),
        "Nouveaux membres d'équipes de soutiens": membres_equipes.filter(
            memberships__created__range=(start, end)
        )
        .distinct()
        .count(),
        "Nouveaux membres d'équipes de soutiens (non insoumis)": membres_equipes.filter(
            memberships__created__range=(start, end)
        )
        .filter(is_insoumise=False)
        .distinct()
        .count(),
    }


def get_events_by_subtype(start, end):
    subtypes = {s.pk: s.label for s in EventSubtype.objects.all()}
    return {
        subtypes[c["subtype"]]: c["count"]
        for c in Event.objects.values("subtype").annotate(count=Count("subtype"))
    }


def get_instant_stats():
    return {
        "Groupes d'action": SupportGroup.objects.filter(
            type=SupportGroup.TYPE_LOCAL_GROUP, published=True
        ).count(),
        "Membres de groupes d'action": Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_LOCAL_GROUP,
            supportgroups__published=True,
        )
        .distinct()
        .count(),
        "Groupes d'action certifiés": SupportGroup.objects.certified().count(),
        "Membres de groupes d'action certifiés": Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_LOCAL_GROUP,
            supportgroups__subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES,
            supportgroups__published=True,
        )
        .distinct()
        .count(),
        "Équipes de soutien": SupportGroup.objects.active()
        .filter(type=SupportGroup.TYPE_2022)
        .count(),
        "Membres d'équipes de soutien": Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_2022, supportgroups__published=True,
        )
        .distinct()
        .count(),
        "Membres d'équipes de soutien (non insoumis)": Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_2022, supportgroups__published=True,
        )
        .filter(is_insoumise=False)
        .distinct()
        .count(),
    }
