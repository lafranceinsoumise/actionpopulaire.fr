from copy import deepcopy

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import transaction
from django.db.models import Count

from agir.lib.tasks import geocode_person
from agir.people.actions.subscription import (
    save_subscription_information,
    SUBSCRIPTIONS_EMAILS,
    SUBSCRIPTION_TYPE_NSP,
)
from agir.people.models import Person
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest
from agir.voting_proxies.tasks import (
    send_voting_proxy_request_confirmation,
    send_voting_proxy_request_accepted_text_messages,
)


def create_or_update_voting_proxy_request(data):
    data = deepcopy(data)
    email = data.pop("email")
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
    email = data.pop("email")

    person_data = {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "date_of_birth": data.get("date_of_birth", ""),
        "email": email,
        "contact_phone": data.get("contact_phone", ""),
        "is_2022": True,
    }

    if data.get("commune", None) and data["commune"].codes_postaux.exists():
        person_data["location_zip"] = data["commune"].codes_postaux.first().code

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
            person, SUBSCRIPTION_TYPE_NSP, person_data, new=is_new_person
        )

        data["voting_dates"] = list(data.get("voting_dates"))
        voting_proxy, created = VotingProxy.objects.update_or_create(
            email=email, defaults={**data, "person_id": person.pk}
        )

    if is_new_person and "welcome" in SUBSCRIPTIONS_EMAILS[SUBSCRIPTION_TYPE_NSP]:
        from agir.people.tasks import send_welcome_mail

        send_welcome_mail.delay(person.pk, type=SUBSCRIPTION_TYPE_NSP)

    if person.coordinates_type is None:
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


def get_voting_proxy_requests_for_proxy(voting_proxy, voting_proxy_request_pks):
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        status=VotingProxyRequest.STATUS_CREATED,
        voting_date__in=voting_proxy.available_voting_dates,
        commune_id=voting_proxy.commune_id,
        consulate_id=voting_proxy.consulate_id,
        proxy__isnull=True,
    )

    if len(voting_proxy_request_pks) > 0:
        voting_proxy_requests = voting_proxy_requests.filter(
            id__in=voting_proxy_request_pks
        )

    # group by email to prioritize requests with the greatest matching date count
    voting_proxy_requests = (
        voting_proxy_requests.values("email")
        .annotate(ids=ArrayAgg("id"))
        .annotate(matching_date_count=Count("voting_date"))
        .order_by("-matching_date_count")
    )

    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist

    return VotingProxyRequest.objects.filter(
        id__in=voting_proxy_requests.first()["ids"]
    ).values(
        "id",
        "first_name",
        "polling_station_number",
        "commune",
        "consulate",
        "voting_date",
    )


def accept_voting_proxy_requests(voting_proxy, voting_proxy_requests):
    voting_proxy_requests.update(
        status=VotingProxyRequest.STATUS_ACCEPTED, proxy=voting_proxy
    )
    voting_proxy_request_pks = list(voting_proxy_requests.values_list("pk", flat=True))
    send_voting_proxy_request_accepted_text_messages.delay(voting_proxy_request_pks)


def decline_voting_proxy_requests(voting_proxy, voting_proxy_requests):
    voting_proxy.status = VotingProxy.STATUS_UNAVAILABLE
    voting_proxy.save()
