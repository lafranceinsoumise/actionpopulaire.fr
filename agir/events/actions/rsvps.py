import logging
from functools import partial

from django.conf import settings
from django.db import transaction, IntegrityError
from django.db.models import F, Count
from django.utils.translation import gettext as _

from agir.payments.actions.payments import (
    create_payment,
    cancel_payment,
    log_payment_event,
)
from ..apps import EventsConfig
from ..models import RSVP, IdentifiedGuest, JitsiMeeting
from ..tasks import send_rsvp_notification, send_guest_confirmation

logger = logging.getLogger(__name__)


class RSVPException(Exception):
    pass


MESSAGES = {
    "full": _("Cet événement est complet."),
    "finished": _("Cet événement est déjà terminé !"),
    "already_rsvped": _("Vous avez déjà indiqué votre participation à cet événement."),
    "forbidden_to_add_guest": _(
        "Il n'est pas possible d'ajouter des invités à cet événement."
    ),
    "indiviual_guests": _(
        "Cet événement nécessite d'inscrire les invités individuellement"
    ),
    "not_rsvped_cannot_add_guest": _(
        "Vous n'êtes pas inscrit⋅e⋅s à cet événement et ne pouvez donc ajouter un invité."
    ),
    "submission_issue": _(
        "Il y a eu un problème sur le remplissage du formulaire. Merci de retenter de vous inscrire."
    ),
}


def _ensure_can_rsvp(event, number=0):
    """Garantit qu'il est possible de RSVP à cet événement.

    Cette fonction est un noop si c'est bien le cas. Si le RSVP n'est pas possible, elle lève une RSVPException.

    Cette fonction vérifie pour le moment :
    - que l'événement n'est pas terminé
    - que nous la limite éventuelle du nombre de participants n'est pas atteinte.

    :param event: L'événement concerné
    :param number: Le numéro de l'inscription à tester
    :return: None
    :raises: :class:`RSVPException`

    """
    if event.is_past():
        raise RSVPException(MESSAGES["finished"])

    # does not try to prevent race conditions
    if event.max_participants is not None and number:
        current_participants = event.participants
        if current_participants + number > event.max_participants:
            raise RSVPException(MESSAGES["full"])


def _get_meta(event, form_submission, is_guest):
    return {
        "VERSION": "2",
        "event_name": event.name,
        "event_id": str(event.pk),
        "submission_id": form_submission and str(form_submission.pk),
        "is_guest": is_guest,
    }


def _get_rsvp_for_event(event, person, form_submission, paying):
    """Obtient un RSVP correspondant à un couple (événement, personne, soumission de formulaire)

    Si le RSVP existe déjà, il est récupéré, verrouillé (avec un row-level lock) et renvoyé, mais uniquement s'il n'est
    pas encore confirmé

    Si ce n'est pas le cas, il est créé (mais pas sauvegardé en DB).

    S'il y a déjà un RSVP confirmé, la fonction lève un `RSVPException`.

    Si un formulaire est associé à l'événement mais qu'aucune soumission de formulaire n'est fournie, ou au contraire
    s'il y a une soumission mais pas de formulaire associé à l'événement, une `RSVPException` est levée.

    :param event: l'événement concerné
    :param person: la personne concernée
    :param form_submission: l'éventuelle soumission de formulaire (potentiellement `None`)
    :param paying: s'il s'agit d'une participation payante ou pas
    :return: le RSVP (non sauvegardé !)
    :raises: :class:`RSVPException`
    """

    # TODO: add race conditions handling with explicit locking for maximum participants
    # see https://www.caktusgroup.com/blog/2009/05/26/explicit-table-locking-with-postgresql-and-django/
    # for potential solution

    if (event.subscription_form is None) != (form_submission is None):
        raise RSVPException(MESSAGES["submission_issue"])

    try:
        rsvp = RSVP.objects.select_for_update().get(event=event, person=person)

        if rsvp.status == RSVP.STATUS_CONFIRMED:
            raise RSVPException(MESSAGES["already_rsvped"])

        if rsvp.status == RSVP.STATUS_CANCELED:
            _ensure_can_rsvp(event, 1)

    except RSVP.DoesNotExist:
        _ensure_can_rsvp(event, 1)
        rsvp = RSVP(event=event, person=person)

    rsvp.status = RSVP.STATUS_AWAITING_PAYMENT if paying else RSVP.STATUS_CONFIRMED
    rsvp.form_submission = form_submission

    return rsvp


def rsvp_to_free_event(event, person, form_submission=None):
    """RSVP la personne a un événement gratuit.

    La fonction se prémunit contre une situation de double création simultanée du RSVP (et est dans ce cas un noop).

    Si le RSVP a bien été créé, la tâche de notification est programmée.

    :param event:
    :param person:
    :param form_submission:
    :return: `None`
    """
    try:
        with transaction.atomic():
            rsvp = _get_rsvp_for_event(event, person, form_submission, False)
            rsvp.save()
            transaction.on_commit(partial(send_rsvp_notification.delay, rsvp.pk))
    except IntegrityError:
        pass


def rsvp_to_paid_event_and_create_payment(
    event, person, payment_mode, form_submission=None
):
    """RSVP la personne à un événement payant.

    Cette fonction calcule le prix du RSVP, crée le RSVP et le paiement correspondant (s'il n'existe pas encore)

    :param event:
    :param person:
    :param payment_mode:
    :param form_submission:
    :return: Le paiement à effectuer pour confirmer le RSVP
    """
    if event.is_free:
        raise RSVPException(
            "Cet événement est gratuit : aucun paiement n'est donc nécessaire."
        )

    price = event.get_price(form_submission and form_submission.data)

    with transaction.atomic():
        rsvp = _get_rsvp_for_event(event, person, form_submission, True)
        if rsvp.payment is not None:
            if rsvp.payment.mode == payment_mode.id and rsvp.payment.can_retry():
                return rsvp.payment

            if not rsvp.payment.can_cancel():
                raise RSVPException("Ce mode de paiement ne permet pas l'annulation.")

            log_payment_event(
                rsvp.payment,
                event="cancel_payment",
                origin="agir.events.actions.rsvps.rsvp_to_paid_event_and_create_payment",
                user=person.role,
            )
            cancel_payment(rsvp.payment)

        rsvp.payment = create_payment(
            person=person,
            type=EventsConfig.PAYMENT_TYPE,
            mode=payment_mode.id,
            price=price,
            meta=_get_meta(event, form_submission, False),
        )
        log_payment_event(
            rsvp.payment,
            commit=True,
            event="create_payment",
            origin="agir.events.actions.rsvps.rsvp_to_paid_event_and_create_payment",
            user=person.role,
        )
        rsvp.save()

    return rsvp.payment


def validate_payment_for_rsvp(payment):
    """Valide la participation suite au règlement d'un paiement.

    Cette fonction est notamment appelée dans les webhooks liés au paiement par carte, et devrait donc éviter
    de lever des exceptions.

    :param payment: le paiement tout juste réglé

    """

    try:
        rsvp = payment.rsvp
    except RSVP.DoesNotExist:
        return logger.error(
            f"validate_payment_for_rsvp: No RSVP for payment {payment.pk}"
        )

    rsvp.status = RSVP.STATUS_CONFIRMED
    rsvp.save()

    # on programme l'envoi de la notification à la fin de la transaction, pour s'assurer que
    # la tâche Celery s'exécute bien après la fin de la transaction (et voit donc le RSVP mis à jour)
    transaction.on_commit(partial(send_rsvp_notification.delay, rsvp.pk))
    return rsvp


def cancel_payment_for_rsvp(payment):
    try:
        rsvp = payment.rsvp
    except RSVP.DoesNotExist:
        return

    rsvp.status = RSVP.STATUS_CANCELED
    rsvp.save()
    return rsvp


def retry_payment_for_rsvp(payment):
    try:
        rsvp = payment.rsvp
    except RSVP.DoesNotExist:
        return

    rsvp.status = RSVP.STATUS_AWAITING_PAYMENT
    rsvp.save()
    return rsvp


def _add_identified_guest(event, person, submission, status, paying=True):
    """Ajoute un invité identifié à un RSVP.

    TODO: l'argument statut n'est semble-t-il plus nécessaire

    :param event: l'événement concerné
    :param person: la personne qui invite
    :param submission: la soumission de formulaire correspondant à l'invité
    :param status: le status
    :param paying:
    :return:
    """
    if not event.allow_guests:
        raise RSVPException(MESSAGES["forbidden_to_add_guest"])

    if (event.subscription_form is None) != (submission is None):
        raise RSVPException(MESSAGES["submission_issue"])

    try:
        rsvp = RSVP.objects.get(
            event=event,
            person=person,
            status__in=[RSVP.STATUS_CONFIRMED, RSVP.STATUS_AWAITING_PAYMENT],
        )
    except RSVP.DoesNotExist:
        raise RSVPException(MESSAGES["not_rsvped_cannot_add_guest"])

    try:
        guest = IdentifiedGuest.objects.select_for_update().get(
            rsvp__event=event, rsvp__person=person, submission=submission
        )

        if guest.status == RSVP.STATUS_CONFIRMED:
            raise RSVPException(MESSAGES["already_rsvped"])

        if guest.status == RSVP.STATUS_CANCELED:
            _ensure_can_rsvp(event, 1)

    except IdentifiedGuest.DoesNotExist:
        _ensure_can_rsvp(event, 1)
        guest = IdentifiedGuest(rsvp=rsvp, submission=submission, status=status)

    guest.status = RSVP.STATUS_AWAITING_PAYMENT if paying else RSVP.STATUS_CONFIRMED
    RSVP.objects.filter(pk=rsvp.pk).update(guests=F("guests") + 1)

    return guest


def add_free_identified_guest(event, person, submission):
    with transaction.atomic():
        guest = _add_identified_guest(
            event, person, submission, RSVP.STATUS_CONFIRMED, False
        )
        try:
            guest.save()
        except IntegrityError:
            raise RSVPException("Validé deux fois le formulaire.")
    send_guest_confirmation.delay(guest.rsvp_id)
    return guest


def add_paid_identified_guest_and_get_payment(
    event, person, payment_mode, form_submission=None
):
    """Récupère le paiement associé à l'ajout d'un invité à un événement payantx

    :param event:
    :param person:
    :param payment_mode:
    :param form_submission:
    :return:
    """
    price = event.get_price(form_submission and form_submission.data)

    with transaction.atomic():
        guest = _add_identified_guest(
            event, person, form_submission, RSVP.STATUS_AWAITING_PAYMENT
        )

        if guest.payment is not None:
            if guest.payment.mode == payment_mode.id and guest.payment.can_retry():
                return guest.payment

            if not guest.payment.can_cancel():
                raise RSVPException("Ce mode de paiement ne permet pas l'annulation.")

            log_payment_event(
                guest.payment,
                event="cancel_payment",
                origin="agir.events.actions.rsvps.add_paid_identified_guest_and_get_payment",
                user=person.role,
            )
            cancel_payment(guest.payment)

        guest.payment = create_payment(
            person=person,
            type=EventsConfig.PAYMENT_TYPE,
            mode=payment_mode.id,
            price=price,
            meta=_get_meta(event, form_submission, True),
        )
        log_payment_event(
            guest.payment,
            commit=True,
            event="create_payment",
            origin="agir.events.actions.rsvps.add_paid_identified_guest_and_get_payment",
            user=person.role,
        )
        guest.save()

        return guest.payment


def validate_payment_for_guest(payment):
    try:
        guest = payment.identified_guest
    except:
        return logger.error(
            f"validate_payment_for_guest: No identified guest for payment {payment.pk}"
        )

    guest.status = RSVP.STATUS_CONFIRMED
    guest.save()

    # à faire au commit uniquement
    transaction.on_commit(partial(send_guest_confirmation.delay, guest.rsvp_id))

    return guest


def cancel_payment_for_guest(payment):
    try:
        guest = payment.identified_guest
    except:
        return

    guest.status = RSVP.STATUS_CANCELED
    guest.save()


def retry_payment_for_guest(payment):
    try:
        guest = payment.identified_guest
    except:
        return

    guest.status = RSVP.STATUS_AWAITING_PAYMENT
    guest.save()


def get_rsvp(event, person):
    return RSVP.objects.get(event=event, person=person)


def is_participant(event, person):
    return RSVP.objects.filter(
        event=event,
        person=person,
        status__in=[RSVP.STATUS_CONFIRMED, RSVP.STATUS_AWAITING_PAYMENT],
    ).exists()


def set_guest_number(event, person, guests):
    if event.subscription_form is not None or not event.is_free:
        raise RSVPException(MESSAGES["indiviual_guests"])

    with transaction.atomic():
        try:
            rsvp = RSVP.objects.select_for_update().get(
                event=event, person=person, status=RSVP.STATUS_CONFIRMED
            )
        except RSVP.DoesNotExist:
            raise RSVPException(MESSAGES["not_rsvped_cannot_add_guest"])

        additional_guests = max(guests - rsvp.guests, 0)
        _ensure_can_rsvp(event, additional_guests)

        if additional_guests and not event.allow_guests:
            raise RSVPException(MESSAGES["forbidden_to_add_guest"])

        rsvp.guests = guests
        rsvp.save()

    send_guest_confirmation.delay(rsvp.pk)


def payment_description_context_generator(payment):
    guest = False

    try:
        rsvp = payment.rsvp
    except RSVP.DoesNotExist:
        try:
            guest = payment.identified_guest
        except IdentifiedGuest.DoesNotExist:
            event = None
        else:
            event = guest.rsvp.event
            guest = True
    else:
        event = rsvp.event

    return {"payment": payment, "event": event, "guest": guest}


def assign_jitsi_meeting(rsvp):
    if (
        rsvp.event.jitsi_meetings.annotate(members=Count("rsvps"))
        .filter(members__lt=settings.JITSI_GROUP_SIZE)
        .first()
        is None
    ):
        JitsiMeeting.objects.create(event=rsvp.event)

    rsvp.jitsi_meeting = (
        rsvp.event.jitsi_meetings.annotate(members=Count("rsvps"))
        .filter(members__lt=settings.JITSI_GROUP_SIZE)
        .first()
    )
    rsvp.save(update_fields=["jitsi_meeting"])
