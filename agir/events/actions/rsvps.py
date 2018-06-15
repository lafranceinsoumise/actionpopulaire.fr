import logging
from django.db.models import F
from django.db import transaction
from django.utils.translation import ugettext as _

from agir.payments.actions import create_payment, redirect_to_payment
from agir.payments.models import Payment

from ..apps import EventsConfig
from ..models import RSVP, IdentifiedGuest
from ..tasks import send_rsvp_notification, send_guest_confirmation

logger = logging.getLogger(__name__)


class RSVPException(Exception):
    pass


MESSAGES = {
    'full': _("Cet événement est complet."),
    'finished': _("Cet événement est déjà terminé !"),
    'already_rsvped': _("Vous avez déjà indiqué votre participation à cet événement."),
    'forbidden_to_add_guest': _("Il n'est pas possible d'ajouter des invités à cet événement."),
    'indiviual_guests': _("Cet événement nécessite d'inscrire les invités individuellement"),
    'not_rsvped_cannot_add_guest': _(
        "Vous n'êtes pas inscrit⋅e⋅s à cet événement et ne pouvez donc ajouter un invité."),
    'submission_issue': _("Il y a eu un problème sur le remplissage du formulaire. Merci de retenter de vous inscrire.")
}


def _ensure_can_rsvp(event, number=0):
    if event.is_past():
        raise RSVPException(MESSAGES['finished'])

    # does not try to prevent race conditions
    if event.max_participants is not None and number:
        current_participants = event.participants
        if current_participants + number > event.max_participants:
            raise RSVPException(MESSAGES['full'])


def _get_meta(event, form_submission, is_guest):
    return {
        'VERSION': '2',
        'event_name': event.name, 'event_id': str(event.pk),
        'submission_id': form_submission and str(form_submission.pk),
        'is_guest': is_guest
    }


def _get_rsvp_for_event(event, person, form_submission, paying):
    # TODO: add race conditions handling with explicit locking for maximum participants
    # see https://www.caktusgroup.com/blog/2009/05/26/explicit-table-locking-with-postgresql-and-django/
    # for potential solution

    if (event.subscription_form is None) != (form_submission is None):
        raise RSVPException(MESSAGES['submission_issue'])

    try:
        rsvp = RSVP.objects.select_for_update().get(event=event, person=person)

        if rsvp.status == RSVP.STATUS_CONFIRMED:
            raise RSVPException(MESSAGES['already_rsvped'])

        if rsvp.status == RSVP.STATUS_AWAITING_PAYMENT and paying:
            raise RSVPException(MESSAGES['already_rsvped'])

        if rsvp.status == RSVP.STATUS_CANCELED:
            _ensure_can_rsvp(event, 1)

    except RSVP.DoesNotExist:
        _ensure_can_rsvp(event, 1)
        rsvp = RSVP(event=event, person=person)

    rsvp.status = RSVP.STATUS_AWAITING_PAYMENT if paying else RSVP.STATUS_CONFIRMED
    rsvp.form_submission = form_submission

    return rsvp


def rsvp_to_free_event(event, person, form_submission=None):
    with transaction.atomic():
        rsvp = _get_rsvp_for_event(event, person, form_submission, False)
        rsvp.save()
    send_rsvp_notification.delay(rsvp.pk)
    return rsvp


def rsvp_to_paid_event_and_get_payment(event, person, payment_mode, form_submission=None):
    if event.is_free:
        raise RSVPException("Cet événement est gratuit : aucun paiement n'est donc nécessaire.")

    price = event.get_price(form_submission)

    with transaction.atomic():
        rsvp = _get_rsvp_for_event(event, person, form_submission, True)
        payment = create_payment(
            person=person,
            type=EventsConfig.PAYMENT_TYPE,
            mode=payment_mode.id,
            price=price,
            meta=_get_meta(event, form_submission, False)
        )
        rsvp.payment = payment
        rsvp.save()

    return payment


def validate_payment_for_rsvp(payment):
    """Validate participation for paid event

    This function should be used in payment webhooks, and should try to avoid raising any error."""

    try:
        rsvp = payment.rsvp
    except RSVP.DoesNotExist:
        raise RSVPException('No RSVP for this payment')

    rsvp.status = RSVP.STATUS_CONFIRMED
    rsvp.save()
    send_rsvp_notification.delay(rsvp.pk)
    return rsvp


def cancel_payment_for_rsvp(payment):
    try:
        rsvp = payment.rsvp
    except RSVP.DoesNotExist:
        raise RSVPException('No RSVP for this payment')

    rsvp.status = RSVP.STATUS_CANCELED
    rsvp.save()
    return rsvp


def _add_identified_guest(event, person, submission, status):
    if not event.allow_guests:
        raise RSVPException(MESSAGES['forbidden_to_add_guest'])

    if (event.subscription_form is None) != (submission is None):
        raise RSVPException(MESSAGES['submission_issue'])

    try:
        rsvp = RSVP.objects.get(event=event, person=person,
                                status__in=[RSVP.STATUS_CONFIRMED, RSVP.STATUS_AWAITING_PAYMENT])
    except RSVP.DoesNotExist:
        raise RSVPException(MESSAGES['not_rsvped_cannot_add_guest'])

    _ensure_can_rsvp(event, 1)
    RSVP.objects.filter(pk=rsvp.pk).update(guests=F('guests') + 1)
    return IdentifiedGuest(
        rsvp=rsvp, submission=submission, status=status
    )


def add_free_identified_guest(event, person, submission=None):
    with transaction.atomic():
        guest = _add_identified_guest(event, person, submission, RSVP.STATUS_CONFIRMED)
        guest.save()
    send_guest_confirmation.delay(guest.rsvp_id)
    return guest


def add_paid_identified_guest_and_get_payment(event, person, payment_mode, form_submission=None):
    price = event.get_price(form_submission)

    with transaction.atomic():
        guest = _add_identified_guest(event, person, form_submission, RSVP.STATUS_AWAITING_PAYMENT)
        payment = create_payment(
            person=person,
            type=EventsConfig.PAYMENT_TYPE,
            mode=payment_mode.id,
            price=price,
            meta=_get_meta(event, form_submission, True)
        )
        guest.payment = payment
        guest.save()

    return payment


def validate_payment_for_guest(payment):
    try:
        guest = payment.identified_guest
    except:
        raise RSVPException('No identified guest for this payment!')

    guest.status = RSVP.STATUS_CONFIRMED
    guest.save()
    send_guest_confirmation.delay(guest.rsvp_id)

    return guest


def cancel_payment_for_guest(payment):
    try:
        guest = payment.identified_guest
    except:
        raise RSVPException('No identified guest for this payment!')

    guest.status = RSVP.STATUS_CANCELED
    guest.save()


def get_rsvp(event, person):
    return RSVP.objects.get(event=event, person=person)


def is_participant(event, person):
    return RSVP.objects.filter(event=event, person=person, status=RSVP.STATUS_CONFIRMED).exists()


def set_guest_number(event, person, guests):
    if event.subscription_form is not None or not event.is_free:
        raise RSVPException(MESSAGES['indiviual_guests'])

    try:
        rsvp = RSVP.objects.select_for_update().get(event=event, person=person, status=RSVP.STATUS_CONFIRMED)
    except RSVP.DoesNotExist:
        raise RSVPException(MESSAGES['not_rsvped_cannot_add_guest'])

    additional_guests = max(guests - rsvp.guests, 0)
    _ensure_can_rsvp(event, additional_guests)

    if not event.allow_guests:
        raise RSVPException(MESSAGES['forbidden_to_add_guest'])

    rsvp.guests = guests
    rsvp.save()

    send_guest_confirmation.delay(rsvp.pk)
