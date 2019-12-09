from django.apps import AppConfig
from django.db.models import Sum
from django.db.models.functions import Coalesce

from agir.payments.payment_modes import PAYMENT_MODES
from agir.system_pay import AbstractSystemPayPaymentMode
from ..payments.types import (
    register_payment_type,
    PaymentType,
    SubscriptionType,
    register_subscription_type,
    SUBSCRIPTION_TYPES,
)


class DonsConfig(AppConfig):
    name = "agir.donations"

    PAYMENT_TYPE = "don"
    SUBSCRIPTION_TYPE = "don_mensuel"

    def ready(self):
        from .views import (
            ReturnView,
            notification_listener,
            subscription_notification_listener,
        )

        payment_type = PaymentType(
            self.PAYMENT_TYPE,
            "Don",
            ReturnView.as_view(),
            status_listener=notification_listener,
            description_template="donations/description.html",
        )

        monthly_payment_type = PaymentType(
            self.SUBSCRIPTION_TYPE,
            "Don automatique",
            ReturnView.as_view(),
            status_listener=notification_listener,
            description_template="donations/description.html",
        )

        register_payment_type(monthly_payment_type)

        register_payment_type(payment_type)

        def monthly_donation_description_context_generator(subscription):
            from agir.system_pay.models import SystemPayTransaction

            subscription_type = SUBSCRIPTION_TYPES[subscription.type]
            context = {
                "subscription": subscription,
                "subscription_type": subscription_type,
                "national_amount": subscription.price
                - subscription.allocations.all().aggregate(
                    total=Coalesce(Sum("amount"), 0)
                )["total"],
            }
            if isinstance(
                PAYMENT_MODES[subscription.mode], AbstractSystemPayPaymentMode
            ):
                context[
                    "expiry_date"
                ] = subscription.system_pay_subscription.alias.expiry_date

            return context

        subscription_type = SubscriptionType(
            self.SUBSCRIPTION_TYPE,
            "Don mensuel",
            ReturnView.as_view(),
            status_listener=subscription_notification_listener,
            description_template="donations/subscription_description.html",
            description_context_generator=monthly_donation_description_context_generator,
        )

        register_subscription_type(subscription_type)
