from datetime import datetime

from django.http.response import HttpResponseRedirect
from django.template import loader

from agir.people.models import Person
from .models import Payment
from .payment_modes import DEFAULT_MODE
from .types import PAYMENT_TYPES


class PaymentException(Exception):
    pass


def create_payment(*, person=None, type, price, mode=DEFAULT_MODE, meta=None, **kwargs):
    """Generate payment response for person with type and price

    :param person: person that is paying, must have all necessary fields (name and location)
    :param type: type of payment
    :param price: price as a decimal
    :param payement_mode: the mode of payment, as found in module agir.payments.modes
    :param meta: an arbitrary bundle of data that will be sent to the payment provider
    :return: an HTTP response
    """
    if meta is None:
        meta = {}

    person_fields = [
        "first_name",
        "last_name",
        "email",
        "location_address1",
        "location_address2",
        "location_zip",
        "location_state",
        "location_city",
        "location_country",
    ]

    if person is not None:
        for f in person_fields:
            kwargs.setdefault(f, getattr(person, f))
        kwargs.setdefault("phone_number", person.contact_phone)

    return Payment.objects.create(
        person=person, type=type, mode=mode, price=price, meta=meta, **kwargs
    )


def complete_payment(payment):
    if payment.status == Payment.STATUS_CANCELED:
        raise PaymentException("Le paiement a déjà été annulé.")

    payment.status = Payment.STATUS_COMPLETED
    payment.save()


def cancel_payment(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        raise PaymentException("Le paiement a déjà été confirmé.")

    payment.status = Payment.STATUS_CANCELED
    payment.save()


def redirect_to_payment(payment):
    return HttpResponseRedirect(payment.get_payment_url())


def notify_status_change(payment):
    # call the registered listener for this event type if there is one to notify it of the changes in status
    if payment.type in PAYMENT_TYPES and PAYMENT_TYPES[payment.type].status_listener:
        PAYMENT_TYPES[payment.type].status_listener(payment)


def default_description_context_generator(payment):
    payment_type = PAYMENT_TYPES[payment.type]
    return {"payment": payment, "payment_type": payment_type}


def description_for_payment(payment):
    if payment.type in PAYMENT_TYPES:
        payment_type = PAYMENT_TYPES[payment.type]
        template_name = (
            payment_type.description_template or "payments/default_description.html"
        )
        context_generator = (
            payment_type.description_context_generator
            or default_description_context_generator
        )
    else:
        template_name = "payments/default_description.html"
        context_generator = default_description_context_generator

    return loader.render_to_string(template_name, context_generator(payment))


def find_or_create_person_from_payment(payment):
    if payment.person is None:
        try:
            payment.person = Person.objects.get_by_natural_key(payment.email)
            if payment.meta.get("subscribed"):
                payment.person.subscribed = True
                payment.person.save()
        except Person.DoesNotExist:
            person_fields = [f.name for f in Person._meta.get_fields()]
            person_kwargs = {
                k: v for k, v in payment.meta.items() if k in person_fields
            }

            if "date_of_birth" in person_kwargs:
                person_kwargs["date_of_birth"] = datetime.strptime(
                    person_kwargs["date_of_birth"], "%d/%m/%Y"
                ).date()

            payment.person = Person.objects.create_person(
                email=payment.email, is_insoumise=False, **person_kwargs
            )
        payment.save()
