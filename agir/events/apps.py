from django.apps import AppConfig

from ..payments.types import register_payment_type


class EventsConfig(AppConfig):
    name = 'agir.events'

    PAYMENT_TYPE = 'evenement'

    def ready(self):
        from .views import PaidEventView, notification_listener
        register_payment_type(self.PAYMENT_TYPE, 'Événement payant', PaidEventView.as_view(), status_listener=notification_listener)
