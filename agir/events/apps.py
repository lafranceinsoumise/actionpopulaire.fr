from django.apps import AppConfig

from ..payments.types import register_payment_type, PaymentType


DEFAULT_ADMIN_MODES = ["system_pay", "check_events", "money", "tpe"]


def admin_payment_modes(payment):
    from .models import RSVP

    try:
        event = payment.rsvp.event
    except RSVP.DoesNotExist:
        pass
    else:
        if (
            event.payment_parameters is not None
            and "admin_payment_modes" in event.payment_parameters
        ):
            return event.payment_parameters["admin_payment_modes"]

    return DEFAULT_ADMIN_MODES


class EventsConfig(AppConfig):
    name = "agir.events"
    verbose_name = "Événements"

    PAYMENT_TYPE = "evenement"

    def ready(self):
        from .views import EventPaidView, notification_listener
        from .actions.rsvps import payment_description_context_generator

        # noinspection PyUnresolvedReferences
        from . import signals

        payment_type = PaymentType(
            self.PAYMENT_TYPE,
            "Événement payant",
            EventPaidView.as_view(),
            status_listener=notification_listener,
            description_template="events/payment_description.html",
            description_context_generator=payment_description_context_generator,
            admin_modes=admin_payment_modes,
        )

        register_payment_type(payment_type)
