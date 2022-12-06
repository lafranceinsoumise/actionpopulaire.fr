from django.utils import timezone

from agir.donations.apps import DonsConfig
from agir.payments.models import Payment


def convert_to_donation(
    payment,
    fiscal_resident,
):
    today = timezone.now().date()
    person = payment.person

    assert payment.type != DonsConfig.SINGLE_TIME_DONATION_TYPE
    assert payment.status == Payment.STATUS_COMPLETED

    # seuls les personnes de nationalité françaises, ou résidents fiscaux en France
    # peuvent donner
    assert "nationality" in person.meta
    assert person.meta["nationality"] == "FR" or (
        fiscal_resident and person.location_country == "FR"
    )
    assert person.first_name and person.last_name
    assert person.location_address1 and person.location_zip and person.location_city
    assert person.contact_phone

    payment.meta.update(
        {
            "changes": f"Transformé en don le {today.strftime('%d/%m/%Y')}.",
            "first_name": person.first_name,
            "last_name": person.last_name,
            "location_address1": person.location_address1,
            "location_address2": person.location_address2,
            "location_zip": person.location_zip,
            "location_city": person.location_city,
            "location_country": str(person.location_country),
            "contact_phone": person.contact_phone.as_e164,
            "nationality": person.meta["nationality"],
            "fiscal_resident": fiscal_resident,
        }
    )
    payment.first_name = person.first_name
    payment.last_name = person.last_name
    payment.email = person.email
    payment.type = DonsConfig.SINGLE_TIME_DONATION_TYPE
    payment.save(update_fields=["first_name", "last_name", "email", "type", "meta"])
