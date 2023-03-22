from datetime import timedelta

from django.conf import settings
from django.db.models import Count, Case, When
from django.utils.timezone import now
from nuntius.models import CampaignSentEvent

from agir.events.models import Event, EventSubtype
from agir.groups.models import SupportGroup, Membership
from agir.people.actions.subscription import (
    SUBSCRIPTION_TYPE_NSP,
    SUBSCRIPTION_TYPE_AP,
    SUBSCRIPTION_TYPE_LFI,
)
from agir.people.model_fields import NestableKeyTextTransform
from agir.people.models import Person
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest

EVENT_SUBTYPES = {"porte-a-porte": 9, "caravane": 4, "inscription-listes": 5}
SORTED_SUBSCRIPTION_TYPES = (
    SUBSCRIPTION_TYPE_NSP,
    SUBSCRIPTION_TYPE_AP,
    SUBSCRIPTION_TYPE_LFI,
)


def get_general_stats(start, end):
    nouveaux_soutiens = (
        Person.objects.filter(is_2022=True, meta__subscriptions__isnull=False)
        .annotate(
            datetime=Case(
                *(
                    When(
                        **{
                            f"meta__subscriptions__{subscription_type}__date__isnull": False,
                            "then": NestableKeyTextTransform(
                                "meta", "subscriptions", subscription_type, "date"
                            ),
                        }
                    )
                    for subscription_type in SORTED_SUBSCRIPTION_TYPES
                ),
                default=None,
            )
        )
        .exclude(datetime__isnull=True)
        .filter(datetime__range=(start.isoformat(), end.isoformat()))
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
        "soutiens_2022": nouveaux_soutiens.count(),
        "soutiens_2022_insoumis": nouveaux_soutiens.filter(is_insoumise=True).count(),
        "soutiens_2022_non_insoumis": nouveaux_soutiens.filter(
            is_insoumise=False
        ).count(),
        "news_LFI": ouvert_news.filter(is_insoumise=True).distinct().count(),
        "taux_news_LFI": sent_events.filter(
            subscriber__is_insoumise=True,
            open_count__gt=0,
        ).count()
        / (sent_events.filter(subscriber__is_insoumise=True).count() or 1)
        * 100,
        "news_2022": ouvert_news.filter(is_insoumise=False).distinct().count(),
        "taux_news_2022": sent_events.filter(
            subscriber__is_insoumise=False,
            open_count__gt=0,
        ).count()
        / (
            sent_events.filter(
                subscriber__is_insoumise=False,
            ).count()
            or 1
        )
        * 100,
        "ap_users": ap_users.count(),
        "ap_users_LFI": ap_users.filter(is_insoumise=True).count(),
        "ap_users_2022": ap_users.filter(is_insoumise=False, is_2022=True).count(),
        "ap_events": Event.objects.filter(
            visibility=Event.VISIBILITY_PUBLIC, start_time__range=(start, end)
        ).count(),
        # Event count by subtype
        **{
            f"ap_events__{key}": Event.objects.public()
            .filter(subtype_id=subtype_id, start_time__range=(start, end))
            .count()
            for key, subtype_id in EVENT_SUBTYPES.items()
        },
        "ga": SupportGroup.objects.active()
        .filter(type=SupportGroup.TYPE_LOCAL_GROUP, created__range=(start, end))
        .count(),
        "membres_ga": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True,
            memberships__created__range=(start, end),
        )
        .distinct()
        .count(),
        "membres_ga_actifs": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True,
            memberships__created__range=(start, end),
            memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        .distinct()
        .count(),
        "membres_ga_contacts": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True,
            memberships__created__range=(start, end),
            memberships__membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER,
        )
        .distinct()
        .count(),
        "liaisons": Person.objects.liaisons(from_date=start, to_date=end).count(),
        "liaisons_contacts": Person.objects.liaisons(from_date=start, to_date=end)
        .filter(meta__subscriptions__AP__subscriber__isnull=False)
        .count(),
        "liaisons_auto": Person.objects.liaisons(from_date=start, to_date=end)
        .exclude(meta__subscriptions__AP__subscriber__isnull=False)
        .count(),
        "contacts": Person.objects.filter(
            meta__subscriptions__AP__subscriber__isnull=False,
            meta__subscriptions__AP__date__gt=start.isoformat(),
            meta__subscriptions__AP__date__lt=end.isoformat(),
        ).count(),
        "voting_proxy_candidates": VotingProxy.objects.filter(
            status=VotingProxy.STATUS_INVITED, created__range=(start, end)
        ).count(),
        "voting_proxies": VotingProxy.objects.filter(
            status__in=(VotingProxy.STATUS_CREATED, VotingProxy.STATUS_AVAILABLE),
            created__range=(start, end),
        ).count(),
        "voting_proxy_requests": VotingProxyRequest.objects.filter(
            created__range=(start, end)
        ).count(),
        "voting_proxy_requests__created": VotingProxyRequest.objects.filter(
            status=VotingProxyRequest.STATUS_CREATED, created__range=(start, end)
        ).count(),
        "voting_proxy_requests__accepted": VotingProxyRequest.objects.filter(
            status=VotingProxyRequest.STATUS_ACCEPTED, created__range=(start, end)
        ).count(),
        "voting_proxy_requests__confirmed": VotingProxyRequest.objects.filter(
            status=VotingProxyRequest.STATUS_CONFIRMED, created__range=(start, end)
        ).count(),
    }


def get_events_by_subtype(start, end):
    subtypes = {s.pk: s.label for s in EventSubtype.objects.all()}
    return {
        subtypes[c["subtype"]]: c["count"]
        for c in Event.objects.values("subtype").annotate(count=Count("subtype"))
    }


def get_instant_stats():
    return {
        "soutiens_2022": Person.objects.filter(is_2022=True).count(),
        "soutiens_2022_insoumis": Person.objects.filter(
            is_2022=True, is_insoumise=True
        ).count(),
        "soutiens_2022_non_insoumis": Person.objects.filter(
            is_2022=True, is_insoumise=False
        ).count(),
        "ga": SupportGroup.objects.filter(
            type=SupportGroup.TYPE_LOCAL_GROUP, published=True
        ).count(),
        "ga_certifies": SupportGroup.objects.certified().filter(published=True).count(),
        "membres_ga": Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_LOCAL_GROUP,
            supportgroups__published=True,
        )
        .distinct()
        .count(),
        "membres_ga_certifies": Person.objects.filter(
            supportgroups__type=SupportGroup.TYPE_LOCAL_GROUP,
            supportgroups__subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES,
            supportgroups__published=True,
        )
        .distinct()
        .count(),
        "membres_ga_actifs": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True,
            memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        .distinct()
        .count(),
        "membres_ga_certifies_actifs": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            supportgroups__subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES,
            memberships__supportgroup__published=True,
            memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        .distinct()
        .count(),
        "membres_ga_contacts": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True,
            memberships__membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER,
        )
        .distinct()
        .count(),
        "membres_ga_certifies_contacts": Person.objects.filter(
            memberships__supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
            memberships__supportgroup__published=True,
            supportgroups__subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES,
            memberships__membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER,
        )
        .distinct()
        .count(),
        "insoumis_non_2022": Person.objects.filter(
            is_insoumise=True,
            is_2022=False,
            emails___bounced=False,
            newsletters__contains=[Person.NEWSLETTER_LFI],
        ).count(),
        "insoumis_non_2022_newsletter": Person.objects.filter(
            is_insoumise=True,
            is_2022=False,
            emails___bounced=False,
            newsletters__contains=[Person.NEWSLETTER_LFI],
            campaignsentevent__datetime__gt=(now() - timedelta(days=90)),
            campaignsentevent__open_count__gt=0,
        )
        .distinct()
        .count(),
        "insoumis_non_2022_phone": Person.objects.filter(
            is_insoumise=True,
            is_2022=False,
            newsletters__contains=[Person.NEWSLETTER_LFI],
        )
        .exclude(contact_phone="")
        .count(),
        "liaisons": Person.objects.liaisons().count(),
        "liaisons_contacts": Person.objects.liaisons()
        .filter(meta__subscriptions__AP__subscriber__isnull=False)
        .count(),
        "liaisons_auto": Person.objects.liaisons()
        .exclude(meta__subscriptions__AP__subscriber__isnull=False)
        .count(),
        "contacts": Person.objects.filter(
            meta__subscriptions__AP__subscriber__isnull=False
        ).count(),
        "voting_proxy_candidates": VotingProxy.objects.filter(
            status=VotingProxy.STATUS_INVITED
        ).count(),
        "voting_proxies": VotingProxy.objects.filter(
            status__in=(VotingProxy.STATUS_CREATED, VotingProxy.STATUS_AVAILABLE),
        ).count(),
        "voting_proxy_requests": VotingProxyRequest.objects.filter().count(),
        "voting_proxy_requests__created": VotingProxyRequest.objects.filter(
            status=VotingProxyRequest.STATUS_CREATED
        ).count(),
        "voting_proxy_requests__accepted": VotingProxyRequest.objects.filter(
            status=VotingProxyRequest.STATUS_ACCEPTED
        ).count(),
        "voting_proxy_requests__confirmed": VotingProxyRequest.objects.filter(
            status=VotingProxyRequest.STATUS_CONFIRMED
        ).count(),
    }
