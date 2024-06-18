from copy import deepcopy
from datetime import timedelta

from data_france.models import Commune
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.postgres.aggregates import ArrayAgg
from django.db import transaction
from django.db.models import Count, Q, Case, When, Value
from django.db.models.functions import Coalesce
from django.utils import timezone

from agir.lib.tasks import geocode_person
from agir.people.actions.subscription import (
    save_subscription_information,
    SUBSCRIPTIONS_EMAILS,
    SUBSCRIPTION_TYPE_AP,
)
from agir.people.models import Person
from agir.voting_proxies import tasks
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest
from agir.voting_proxies.tasks import (
    send_voting_proxy_request_confirmation,
    send_voting_proxy_request_accepted_text_messages,
    send_voting_proxy_request_confirmed_text_messages,
    send_cancelled_request_to_voting_proxy,
    send_cancelled_request_acceptation_to_request_owner,
)

PROXY_TO_REQUEST_DISTANCE_LIMIT = 20  # 20 KM
PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT = 10


def create_or_update_voting_proxy_request(data):
    data = deepcopy(data)
    email = data.pop("email").lower()
    voting_dates = data.pop("votingDates")
    updated = False
    voting_proxy_request_pks = []

    for voting_date in voting_dates:
        (voting_proxy_request, created) = VotingProxyRequest.objects.update_or_create(
            voting_date=voting_date,
            email=email,
            defaults={**data},
        )
        voting_proxy_request_pks.append(voting_proxy_request.id)
        if not created:
            updated = True

    data.update({"email": email, "votingDates": voting_dates, "updated": updated})
    send_voting_proxy_request_confirmation.delay(voting_proxy_request_pks)

    return data


def create_or_update_voting_proxy(data):
    data["voting_dates"] = list(data.get("voting_dates"))
    email = data.pop("email").lower()
    subscribed = data.pop("subscribed", False)

    person_data = {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "date_of_birth": data.get("date_of_birth", ""),
        "email": email,
        "contact_phone": data.get("contact_phone", ""),
    }

    with transaction.atomic():
        is_new_person = False
        try:
            with transaction.atomic():
                person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            person = Person.objects.create_person(**person_data)
            is_new_person = True

        person_data["newsletters"] = data.pop("newsletters", [])
        save_subscription_information(
            person, SUBSCRIPTION_TYPE_AP, person_data, new=is_new_person
        )

        if subscribed and not person.subscribed:
            person.subscribed = True

        if subscribed and not person.is_political_support:
            person.is_political_support = True

        # Update person address if needed
        address = data.pop("address", None)
        city = data.pop("city", None)
        zip = data.pop("zip", None)
        if address:
            person.location_address1 = address
        if city:
            person.location_city = city
        if zip:
            person.location_zip = zip
        elif data.get("commune", None) and data["commune"].codes_postaux.exists():
            person.location_zip = data["commune"].codes_postaux.first().code
        person.save()

        voting_proxy, created = VotingProxy.objects.update_or_create(
            person_id=person.pk, defaults={**data, "email": email}
        )
        if voting_proxy.status in [
            VotingProxy.STATUS_INVITED,
            VotingProxy.STATUS_UNAVAILABLE,
        ]:
            voting_proxy.status = VotingProxy.STATUS_CREATED
            voting_proxy.save()

    if (
        is_new_person
        and subscribed
        and "welcome" in SUBSCRIPTIONS_EMAILS[SUBSCRIPTION_TYPE_AP]
    ):
        from agir.people.tasks import send_welcome_mail

        send_welcome_mail.delay(person.pk, SUBSCRIPTION_TYPE_AP)

    geocode_person.delay(person.pk)
    data.update(
        {
            "id": voting_proxy.id,
            "updated": not created,
            "person_id": person.id,
            "email": email,
            "status": voting_proxy.status,
        }
    )

    return data


def update_voting_proxy(instance, data):
    if "voting_dates" in data:
        data["voting_dates"] = list(data.get("voting_dates"))
    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    return instance


def get_acceptable_voting_proxy_requests_for_proxy(
    voting_proxy, voting_proxy_request_pks=None
):
    voting_proxy_requests = (
        VotingProxyRequest.objects.pending()
        .filter(voting_date__in=voting_proxy.available_voting_dates)
        .exclude(email=voting_proxy.email)
    )

    if voting_proxy_request_pks:
        voting_proxy_requests = voting_proxy_requests.filter(
            id__in=voting_proxy_request_pks
        )

    if not voting_proxy_requests.exists():
        return

    # Use consulate match for non-null consulate proxies
    if voting_proxy.consulate_id is not None:
        voting_proxy_requests = voting_proxy_requests.filter(
            consulate_id=voting_proxy.consulate_id,
        ).annotate(distance=Value(0))
    # Use voting_proxy person address to request commune distance,
    # fallback to commune match for non-null commune proxies
    else:
        near_requests = None
        if voting_proxy.person and voting_proxy.person.coordinates:
            near_requests = (
                voting_proxy_requests.filter(commune__mairie_localisation__isnull=False)
                .filter(
                    commune__mairie_localisation__dwithin=(
                        voting_proxy.person.coordinates,
                        D(
                            km=min(
                                voting_proxy.person.action_radius,
                                PROXY_TO_REQUEST_DISTANCE_LIMIT,
                            )
                        ),
                    )
                )
                .annotate(
                    distance=Distance(
                        "commune__mairie_localisation", voting_proxy.person.coordinates
                    )
                )
            )
        if near_requests and near_requests.exists():
            voting_proxy_requests = near_requests
        else:
            voting_proxy_requests = voting_proxy_requests.filter(
                commune_id=voting_proxy.commune_id,
            ).annotate(distance=Value(0))

    voting_proxy_requests = voting_proxy_requests.annotate(
        polling_station_match=Case(
            When(
                commune_id=voting_proxy.commune_id,
                polling_station_number__isnull=False,
                polling_station_number__iexact=voting_proxy.polling_station_number,
                then=1,
            ),
            default=0,
        )
    )

    # group by email to prioritize requests with the greatest matching date count
    voting_proxy_requests = (
        voting_proxy_requests.values("email")
        .annotate(ids=ArrayAgg("id"))
        .annotate(voting_dates=ArrayAgg("voting_date"))
        .annotate(matching_date_count=Count("voting_date"))
        .order_by("distance", "-polling_station_match", "-matching_date_count")
    )

    return voting_proxy_requests


def get_voting_proxy_requests_for_proxy(voting_proxy, voting_proxy_request_pks):
    voting_proxy_requests = get_acceptable_voting_proxy_requests_for_proxy(
        voting_proxy, voting_proxy_request_pks
    )

    if not voting_proxy_requests or not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist

    return VotingProxyRequest.objects.filter(
        id__in=voting_proxy_requests.first()["ids"]
    ).order_by("voting_date")


def accept_single_voting_proxy_request(voting_proxy, voting_proxy_request):
    with transaction.atomic():
        voting_proxy_request.status = VotingProxyRequest.STATUS_ACCEPTED
        voting_proxy_request.proxy = voting_proxy
        voting_proxy_request.save()

        voting_proxy.status = VotingProxy.STATUS_AVAILABLE
        voting_proxy.save()

    send_voting_proxy_request_accepted_text_messages.delay(
        [voting_proxy_request.pk],
    )


def accept_voting_proxy_requests(voting_proxy, voting_proxy_requests):
    with transaction.atomic():
        voting_proxy_requests.update(
            status=VotingProxyRequest.STATUS_ACCEPTED, proxy=voting_proxy
        )

        voting_proxy.status = VotingProxy.STATUS_AVAILABLE
        voting_proxy.save()

    send_voting_proxy_request_accepted_text_messages.delay(
        list(voting_proxy_requests.values_list("pk", flat=True)),
    )


def mark_voting_proxy_as_unavailable(voting_proxy, *args, **kwargs):
    voting_proxy.status = VotingProxy.STATUS_UNAVAILABLE
    voting_proxy.save()


def confirm_voting_proxy_requests(voting_proxy_requests):
    voting_proxy_request_pks = list(voting_proxy_requests.values_list("pk", flat=True))
    voting_proxy_requests.update(status=VotingProxyRequest.STATUS_CONFIRMED)
    send_voting_proxy_request_confirmed_text_messages.delay(voting_proxy_request_pks)


def cancel_voting_proxy_requests(voting_proxy_requests):
    for request in voting_proxy_requests:
        if request.proxy is not None:
            send_cancelled_request_to_voting_proxy.delay(
                request.pk, request.proxy.email
            )
    voting_proxy_requests.update(status=VotingProxyRequest.STATUS_CANCELLED, proxy=None)


def cancel_voting_proxy_request_acceptation(voting_proxy_requests):
    for request in voting_proxy_requests:
        if request.proxy is not None:
            send_cancelled_request_acceptation_to_request_owner.delay(
                request.pk, request.proxy.first_name
            )
    voting_proxy_requests.update(status=VotingProxyRequest.STATUS_CREATED, proxy=None)


def send_matching_requests_to_proxy(proxy, matching_request_ids):
    proxy.last_matched = timezone.now()
    proxy.save()
    tasks.send_matching_request_to_voting_proxy.delay(
        proxy.id, list(matching_request_ids)
    )


def match_available_proxies_with_requests(
    pending_requests, notify_proxy=send_matching_requests_to_proxy
):
    fulfilled_request_ids = []
    pending_request_ids = list(pending_requests.values_list("id", flat=True))

    # Retrieve all available proxy that has not been matched in the last two days
    available_proxies = (
        VotingProxy.objects.reliable()
        .select_related("person")
        .order_by(
            "-voting_dates__len",
            Coalesce("last_matched", Value("2022-01-01 00:00:00")).asc(),
        )
    )

    # Try to match available voting proxies with pending requests
    for proxy in available_proxies:
        if len(pending_request_ids) == 0:
            break
        try:
            matching_request_ids = get_voting_proxy_requests_for_proxy(
                proxy, pending_request_ids
            ).values_list("id", flat=True)
        except VotingProxyRequest.DoesNotExist:
            pass
        else:
            notify_proxy(proxy, matching_request_ids)
            fulfilled_request_ids += matching_request_ids
            pending_request_ids = [
                pending_request_id
                for pending_request_id in pending_request_ids
                if pending_request_id not in fulfilled_request_ids
            ]

    return fulfilled_request_ids


def invite_voting_proxy_candidates(candidates, request):
    voting_proxy_candidates = [
        VotingProxy(
            status=VotingProxy.STATUS_INVITED,
            person=candidate,
            email=candidate.email,
            first_name=candidate.first_name if candidate.first_name else "-",
            last_name=candidate.last_name if candidate.first_name else "-",
            contact_phone=candidate.contact_phone if candidate.first_name else "-",
            polling_station_number="",
        )
        for candidate in candidates
    ]
    voting_proxy_candidates = VotingProxy.objects.bulk_create(
        voting_proxy_candidates, ignore_conflicts=True
    )
    voting_proxy_candidates_ids = [
        voting_proxy_candidate.pk for voting_proxy_candidate in voting_proxy_candidates
    ]
    voting_proxy_candidates_emails = [
        voting_proxy_candidate.email
        for voting_proxy_candidate in voting_proxy_candidates
    ]
    tasks.send_voting_proxy_candidate_invitation_email.delay(
        voting_proxy_candidates_emails
    )

    return voting_proxy_candidates_ids


def get_voting_proxy_candidates_queryset(request, blacklist_ids):
    candidates = (
        Person.objects.exclude(role__isnull=False, role__is_active=False)
        .exclude(emails__address=None)
        .exclude(voting_proxy__isnull=False)
        .filter(is_political_support=True, newsletters__len__gt=0)
    )

    if request and request["email"]:
        candidates = candidates.exclude(emails__address=request["email"])

    if blacklist_ids:
        candidates = candidates.exclude(id__in=blacklist_ids)

    return candidates


def find_voting_proxy_candidates_for_requests(
    pending_requests, send_invitations=invite_voting_proxy_candidates
):
    possibly_fulfilled_request_ids = []
    candidate_ids = []

    # Find candidates for consulate requests
    for request in (
        pending_requests.exclude(consulate__pays__isnull=True)
        .values("email", "consulate__pays")
        .annotate(ids=ArrayAgg("id"))
    ):
        pays = request["consulate__pays"].split(",")
        candidates = get_voting_proxy_candidates_queryset(
            request, candidate_ids
        ).filter(location_country__in=pays)[:PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT]

        if candidates.exists():
            invited_candidate_ids = send_invitations(candidates, request)
            candidate_ids += invited_candidate_ids
            possibly_fulfilled_request_ids += request["ids"]

    # Find candidates for commune requests
    for request in (
        pending_requests.exclude(commune__isnull=True)
        .values("email", "commune_id")
        .annotate(ids=ArrayAgg("id"))
    ):
        commune = Commune.objects.get(id=request["commune_id"])
        candidates = get_voting_proxy_candidates_queryset(request, candidate_ids)
        # Match by distance for geolocalised communes
        if commune.mairie_localisation:
            candidates = candidates.exclude(coordinates__isnull=True).filter(
                coordinates__dwithin=(
                    commune.mairie_localisation,
                    D(km=PROXY_TO_REQUEST_DISTANCE_LIMIT),
                )
            )
        # Try to match by city code / zip code for non-geolocalised communes
        else:
            candidates = (
                candidates.exclude(
                    location_citycode__isnull=True, location_zip__isnull=True
                )
                .filter(
                    Q(location_citycode=commune.code)
                    | Q(
                        location_zip__in=commune.codes_postaux.values_list(
                            "code", flat=True
                        )
                    )
                )
                .distinct()
            )

        if candidates.exists():
            # Give priority with people with the most recent event rsvps
            candidates = candidates.annotate(
                rsvp_count=Count(
                    "rsvps",
                    filter=Q(
                        rsvps__event__end_time__gte=timezone.now() - timedelta(days=365)
                    ),
                    distinct=True,
                )
            ).order_by("-rsvp_count")[:PER_VOTING_PROXY_REQUEST_INVITATION_LIMIT]

            invited_candidate_ids = send_invitations(candidates, request)
            candidate_ids += invited_candidate_ids
            possibly_fulfilled_request_ids += request["ids"]

    return possibly_fulfilled_request_ids, candidate_ids
