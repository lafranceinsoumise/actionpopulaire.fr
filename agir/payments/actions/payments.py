from datetime import datetime

from django.http.response import HttpResponseRedirect
from django.template import loader
from django.utils import timezone

from agir.payments.models import Payment
from agir.payments.payment_modes import DEFAULT_MODE, PAYMENT_MODES
from agir.payments.types import PAYMENT_TYPES
from agir.people.models import Person


class PaymentException(Exception):
    pass


def log_payment_event(payment, commit=False, **kwargs):
    payment.events.append(
        {
            "date": timezone.now().astimezone(timezone.utc).isoformat(),
            **{key: str(val) for key, val in kwargs.items()},
        }
    )

    if commit:
        payment.save()

    return payment


def create_payment(*, person=None, type, price, mode=DEFAULT_MODE, meta=None, **kwargs):
    """Generate payment response for person with type and price

    :param person: person that is paying, must have all necessary fields (name and location)
    :param type: type of payment
    :param price: price as a decimal
    :param mode: the mode of payment, as found in module agir.payments.modes
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
        for field in person_fields:
            kwargs.setdefault(field, getattr(person, field))
        kwargs.setdefault("phone_number", person.contact_phone)
    else:
        for field in person_fields:
            kwargs.setdefault(field, meta.get(field, ""))
        kwargs.setdefault("phone_number", meta.get("contact_phone"))

    return Payment.objects.create(
        person=person, type=type, mode=mode, price=price, meta=meta, **kwargs
    )


def change_payment_status(payment, status):
    if status == Payment.STATUS_COMPLETED:
        complete_payment(payment)
    elif status == Payment.STATUS_REFUSED:
        refuse_payment(payment)
    elif status == Payment.STATUS_CANCELED:
        cancel_payment(payment)
    elif status == Payment.STATUS_REFUND:
        refund_payment(payment)
    elif status == Payment.STATUS_WAITING:
        wait_for_payment(payment)
    else:
        raise ValueError("Ce statut n'existe pas ou n'est pas disponible.")

    notify_status_change(payment)


def wait_for_payment(payment):
    if payment.is_done():
        raise PaymentException("Le paiement a déjà été terminé.")

    if payment.status == Payment.STATUS_WAITING:
        return

    payment.status = Payment.STATUS_WAITING
    payment.save(update_fields=["status", "events"])


def complete_payment(payment):
    if payment.status == Payment.STATUS_CANCELED:
        raise PaymentException("Le paiement a déjà été annulé.")

    if payment.status == Payment.STATUS_REFUND:
        raise PaymentException("Le paiement a déjà été remboursé.")

    payment.status = Payment.STATUS_COMPLETED
    payment.save(update_fields=["status", "events"])


def refuse_payment(payment):
    if payment.status == Payment.STATUS_CANCELED:
        raise PaymentException("Le paiement a déjà été annulé.")

    payment.status = Payment.STATUS_REFUSED
    payment.save(update_fields=["status", "events"])


def cancel_payment(payment):
    if payment.status == Payment.STATUS_COMPLETED:
        raise PaymentException("Le paiement a déjà été confirmé.")

    if payment.is_cancelled():
        return

    payment.status = Payment.STATUS_CANCELED
    payment.save(update_fields=["status", "events"])


def refund_payment(payment):
    if payment.status not in (Payment.STATUS_COMPLETED, Payment.STATUS_REFUND):
        raise PaymentException("Impossible de rembourser un paiement non confirmé.")

    payment.status = Payment.STATUS_REFUND
    payment.save(update_fields=["status", "events"])


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
    if payment.person is None and payment.email is not None:
        try:
            payment.person = Person.objects.get_by_natural_key(payment.email)
        except Person.DoesNotExist:
            person_fields = [f.name for f in Person._meta.get_fields()]
            person_meta = {k: v for k, v in payment.meta.items() if k in person_fields}
            newsletters = (
                Person.MAIN_NEWSLETTER_CHOICES
                if payment.meta.get("subscr", False)
                else []
            )

            if "date_of_birth" in person_meta:
                person_meta["date_of_birth"] = datetime.strptime(
                    person_meta["date_of_birth"], "%d/%m/%Y"
                ).date()

            if not payment.email:
                payment.email = payment.meta.get("email")

            payment.person = Person.objects.create_person(
                email=payment.email, newsletters=newsletters, **person_meta
            )

        if payment.meta.get("subscribed", False) and not payment.person.subscribed:
            payment.person.subscribed = True

        payment.person.save()
        payment.save()


def cancel_or_refund_payment(payment, *args, **kwargs):
    return PAYMENT_MODES[payment.mode].cancel_or_refund_payment_action(
        payment, *args, **kwargs
    )
