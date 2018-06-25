from django.apps import AppConfig

from ..payments.types import register_payment_type


class EventsConfig(AppConfig):
    name = 'agir.events'

    PAYMENT_TYPE = 'evenement'

    def ready(self):
        from .views import EventPaidView, notification_listener
        from .actions.rsvps import retry_listener
        register_payment_type(
            self.PAYMENT_TYPE,
            'Événement payant',
            EventPaidView.as_view(),
            status_listener=notification_listener,
            retry=retry_listener,
        )
