from django.apps import AppConfig

from ..payments.types import register_payment_type, PaymentType


class EventsConfig(AppConfig):
    name = "agir.events"

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
            admin_modes=["system_pay", "check_events", "money", "tpe"],
        )

        register_payment_type(payment_type)
