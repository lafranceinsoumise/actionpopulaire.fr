from django.apps import AppConfig
from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import Coalesce

from ..payments.types import (
    register_payment_type,
    PaymentType,
    SubscriptionType,
    register_subscription_type,
)


class DonsConfig(AppConfig):
    name = "agir.donations"

    PAYMENT_TYPE = "don"
    SUBSCRIPTION_TYPE = "don_mensuel"

    def ready(self):
        from django.views.generic import RedirectView
        from .views import (
            notification_listener,
            subscription_notification_listener,
        )
        from ..payments.actions.subscriptions import (
            default_description_context_generator,
        )

        payment_type = PaymentType(
            self.PAYMENT_TYPE,
            "Don",
            RedirectView.as_view(url="https://lafranceinsoumise.fr/remerciement-don/"),
            status_listener=notification_listener,
            description_template="donations/description.html",
            matomo_goal=settings.DONATION_MATOMO_GOAL,
        )

        monthly_payment_type = PaymentType(
            self.SUBSCRIPTION_TYPE,
            "Don automatique",
            RedirectView.as_view(url="https://lafranceinsoumise.fr/remerciement-don/"),
            status_listener=notification_listener,
            description_template="donations/description.html",
            matomo_goal=settings.MONTHLY_DONATION_MATOMO_GOAL,
        )

        register_payment_type(monthly_payment_type)

        register_payment_type(payment_type)

        def monthly_donation_description_context_generator(subscription):
            context = default_description_context_generator(subscription)
            context["national_amount"] = (
                subscription.price
                - subscription.allocations.all().aggregate(
                    total=Coalesce(Sum("amount"), 0)
                )["total"],
            )

            return context

        subscription_type = SubscriptionType(
            self.SUBSCRIPTION_TYPE,
            "Don mensuel",
            RedirectView.as_view(url="https://lafranceinsoumise.fr/remerciement-don/"),
            status_listener=subscription_notification_listener,
            description_template="donations/subscription_description.html",
            description_context_generator=monthly_donation_description_context_generator,
        )

        register_subscription_type(subscription_type)
