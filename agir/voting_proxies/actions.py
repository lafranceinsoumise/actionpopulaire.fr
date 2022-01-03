from copy import deepcopy

from django.db import transaction

from agir.lib.tasks import geocode_person
from agir.people.actions.subscription import (
    save_subscription_information,
    SUBSCRIPTIONS_EMAILS,
    SUBSCRIPTION_TYPE_NSP,
)
from agir.people.models import Person
from agir.voting_proxies.models import VotingProxy, VotingProxyRequest
from agir.voting_proxies.tasks import send_voting_proxy_request_confirmation


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
