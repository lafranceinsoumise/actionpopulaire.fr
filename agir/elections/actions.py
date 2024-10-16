from django.db import transaction

from agir.elections.models import PollingStationOfficer
from agir.lib.tasks import geocode_person
from agir.people.actions.subscription import (
    SUBSCRIPTIONS_EMAILS,
    SUBSCRIPTION_TYPE_AP,
)
from agir.people.models import Person

UPDATABLE_PERSON_FIELDS = (
    "date_of_birth",
    "contact_phone",
    "location_address1",
    "location_address2",
    "location_zip",
    "location_city",
    "location_country",
)


def create_or_update_polling_station_officer(data):
    data["available_voting_dates"] = list(data.get("available_voting_dates"))
    email = data.pop("contact_email").lower()

    person_data = {
        "first_name": data.get("first_name", None),
        "last_name": data.get("last_name", None),
        "date_of_birth": data.get("birth_date", None),
        "contact_phone": data.get("contact_phone", ""),
        "location_address1": data.get("location_address1", None),
        "location_address2": data.get("location_address2", None),
        "location_zip": data.get("location_zip", None),
        "location_city": data.get("location_city", None),
        "location_country": data.get("location_country", None),
    }
    person_data = {key: value for key, value in person_data.items() if value}

    with transaction.atomic():
        is_new_person = False
        try:
            person = Person.objects.get_by_natural_key(email)
            for key, value in person_data.items():
                if key in UPDATABLE_PERSON_FIELDS:
                    setattr(person, key, person_data[key])
            person.save()
        except Person.DoesNotExist:
            is_new_person = True
            person = Person.objects.create_person(email=email, **person_data)

        polling_station_officer = PollingStationOfficer.objects.filter(
            person_id=person.pk,
            available_voting_dates__overlap=data["available_voting_dates"],
        )

        if polling_station_officer.exists():
            created = False
            polling_station_officer.update(**data)
            polling_station_officer = polling_station_officer.first()
            polling_station_officer.refresh_from_db()
        else:
            created = True
            polling_station_officer = PollingStationOfficer.objects.create(
                person_id=person.pk, contact_email=email, **data
            )

        geocode_person.delay(person.pk)

        if is_new_person and "welcome" in SUBSCRIPTIONS_EMAILS[SUBSCRIPTION_TYPE_AP]:
            from agir.people.tasks import send_welcome_mail

            send_welcome_mail.delay(person.pk, SUBSCRIPTION_TYPE_AP)

        data.update(
            {
                "id": polling_station_officer.id,
                "updated": not created,
                "person_id": person.id,
                "contact_email": email,
            }
        )

        return data
