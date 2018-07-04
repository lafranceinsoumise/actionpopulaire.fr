from django.http.response import HttpResponseRedirect

from .models import Payment
from .types import PAYMENT_TYPES
from .payment_modes import DEFAULT_MODE


class PaymentException(Exception):
    pass


def create_payment(person, type, price, mode=DEFAULT_MODE, meta=None):
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

    person_fields = ['first_name', 'last_name', 'email', 'location_address1', 'location_address2', 'location_zip',
                     'location_state', 'location_city', 'location_country',]

    return Payment.objects.create(
        person=person,
        type=type,
        mode=mode,
        price=price,
        meta=meta,
        **{f: getattr(person, f) for f in person_fields}
    )

def complete_payment(payment):
    if (payment.status == Payment.STATUS_CANCELED):
        raise PaymentException("Le paiement a déjà été annulé.")

    payment.status = Payment.STATUS_COMPLETED
    payment.save()


def cancel_payment(payment):
    if (payment.status == Payment.STATUS_COMPLETED):
        raise PaymentException("Le paiement a déjà été confirmé.")

    payment.status = Payment.STATUS_CANCELED
    payment.save()


def redirect_to_payment(payment):
    return HttpResponseRedirect(payment.get_payment_url())


def notify_status_change(payment):
    # call the registered listener for this event type if there is one to notify it of the changes in status
    if payment.type in PAYMENT_TYPES and PAYMENT_TYPES[payment.type].status_listener:
        PAYMENT_TYPES[payment.type].status_listener(payment)
