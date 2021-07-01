from datetime import timedelta

from django.conf import settings
from django.db.models import Count
from django.utils.timezone import now
from nuntius.models import CampaignSentEvent

from agir.people.models import Person
from agir.groups.models import SupportGroup, Membership
from agir.events.models import Event, EventSubtype


def get_general_stats(start, end):
    nouveaux_soutiens = Person.objects.filter(
        meta__subscriptions__NSP__date__gt=start.isoformat(),
        meta__subscriptions__NSP__date__lt=end.isoformat(),
    )

    ouvert_news = Person.objects.filter(
        campaignsentevent__datetime__range=(start, end),
        campaignsentevent__open_count__gt=0,
        is_2022=True,
    )

    ap_users = Person.objects.filter(role__last_login__range=(start, end))

    sent_events = CampaignSentEvent.objects.filter(
        subscriber__is_2022=True, datetime__range=(start, end)
    )

    return {
        "soutiens_NSP": nouveaux_soutiens.count(),
        "soutiens_NSP_insoumis": nouveaux_soutiens.filter(is_insoumise=True).count(),
        "soutiens_NSP_non_insoumis": nouveaux_soutiens.filter(
            is_insoumise=False
        ).count(),
        "news_LFI": ouvert_news.filter(is_insoumise=True).distinct().count(),
        "taux_news_LFI": sent_events.filter(
            subscriber__is_insoumise=True, open_count__gt=0,
        ).count()
        / (sent_events.filter(subscriber__is_insoumise=True).count() or 1)
        * 100,
        "news_NSP": ouvert_news.filter(is_insoumise=False).distinct().count(),
        "taux_news_NSP": sent_events.filter(
            subscriber__is_insoumise=False, open_count__gt=0,
        ).count()
        / (sent_events.filter(subscriber__is_insoumise=False,).count() or 1)
        * 100,
        "ap_users": ap_users.count(),
        "ap_users_LFI": ap_users.filter(is_insoumise=True).count(),
        "ap_users_NSP": ap_users.filter(is_insoumise=False, is_2022=True).count(),
        "ap_events": Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC, start_time__range=(start, end)
        ).count(),
        "ap_events_LFI": Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC,
            for_users=Event.FOR_USERS_INSOUMIS,
            start_time__range=(start, end),
        ).count(),
        "ap_events_NSP": Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC,
            for_users=Event.FOR_USERS_2022,
            start_time__range=(start, end),
        ).count(),
        "ga_LFI": SupportGroup.objects.active()
        .filter(type=SupportGroup.TYPE_LOCAL_GROUP, created__range=(start, end))
        .count(),
        "membres_ga_LFI": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True,
        )
        .filter(memberships__created__range=(start, end))
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
        "soutiens_NSP": Person.objects.filter(is_2022=True).count(),
        "soutiens_NSP_insoumis": Person.objects.filter(
            is_2022=True, is_insoumise=True
        ).count(),
        "soutiens_NSP_non_insoumis": Person.objects.filter(
            is_2022=True, is_insoumise=False
        ).count(),
        "ga_LFI": SupportGroup.objects.filter(
            type=SupportGroup.TYPE_LOCAL_GROUP, published=True
        ).count(),
        "ga_LFI_certifies": SupportGroup.objects.certified()
        .filter(published=True)
        .count(),
        "membres_ga_LFI": Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_LOCAL_GROUP,
            supportgroups__published=True,
        )
        .distinct()
        .count(),
        "membres_ga_LFI_certifies": Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_LOCAL_GROUP,
            supportgroups__subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES,
            supportgroups__published=True,
        )
        .distinct()
        .count(),
        "insoumis_non_NSP": Person.objects.filter(
            is_insoumise=True,
            is_2022=False,
            emails___bounced=False,
            newsletters__contains=[Person.NEWSLETTER_LFI],
        ).count(),
        "insoumis_non_NSP_newsletter": Person.objects.filter(
            is_insoumise=True,
            is_2022=False,
            emails___bounced=False,
            newsletters__contains=[Person.NEWSLETTER_LFI],
            campaignsentevent__datetime__gt=(now() - timedelta(days=90)),
            campaignsentevent__open_count__gt=0,
        )
        .distinct()
        .count(),
        "insoumis_non_NSP_phone": Person.objects.filter(
            is_insoumise=True,
            is_2022=False,
            newsletters__contains=[Person.NEWSLETTER_LFI],
        )
        .exclude(contact_phone="")
        .count(),
    }
