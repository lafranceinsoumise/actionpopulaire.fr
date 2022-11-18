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

    SINGLE_TIME_DONATION_TYPE = "don"
    MONTHLY_DONATION_TYPE = "don_mensuel"
    CONTRIBUTION_TYPE = "contribution"

    TYPE_CHOICES = (
        (SINGLE_TIME_DONATION_TYPE, "don ponctuel"),
        (MONTHLY_DONATION_TYPE, "don mensuel"),
        (CONTRIBUTION_TYPE, "contribution"),
    )

    def ready(self):
        from django.urls import reverse_lazy
        from django.views.generic import RedirectView
        from .views import (
            notification_listener,
            subscription_notification_listener,
        )

        def payment_description_context_generator(payment):
            from .allocations import get_allocation_list
            from agir.payments.actions.payments import (
                default_description_context_generator,
            )

            context = default_description_context_generator(payment)
            allocations = get_allocation_list(
                payment.meta.get("allocations", []), with_labels=True
            )
            if allocations:
                context["allocations"] = allocations
                allocation_amount = sum(
                    [allocation.get("amount") for allocation in allocations]
                )
                context["national_amount"] = payment.price - allocation_amount

            return context

        def subscription_description_context_generator(subscription):
            from agir.payments.actions.subscriptions import (
                default_description_context_generator,
            )

            context = default_description_context_generator(subscription)
            allocation_amount = subscription.allocations.all().aggregate(
                total=Coalesce(Sum("amount"), 0)
            )["total"]
            context["national_amount"] = subscription.price - allocation_amount

            return context

        ## SINGLE TIME DONATIONS
        single_time_donation_payment_type = PaymentType(
            self.SINGLE_TIME_DONATION_TYPE,
            "Don",
            RedirectView.as_view(url=reverse_lazy("donation_success")),
            status_listener=notification_listener,
            description_template="donations/description.html",
            description_context_generator=payment_description_context_generator,
            matomo_goal=settings.DONATION_MATOMO_GOAL,
        )

        register_payment_type(single_time_donation_payment_type)

        ## MONTHLY DONATIONS
        monthly_donation_payment_type = PaymentType(
            self.MONTHLY_DONATION_TYPE,
            "Don mensuel",
            RedirectView.as_view(url=reverse_lazy("donation_success")),
            status_listener=notification_listener,
            description_template="donations/description.html",
            description_context_generator=payment_description_context_generator,
            matomo_goal=settings.MONTHLY_DONATION_MATOMO_GOAL,
        )

        register_payment_type(monthly_donation_payment_type)

        monthly_donation_subscription_type = SubscriptionType(
            self.MONTHLY_DONATION_TYPE,
            "Don mensuel",
            RedirectView.as_view(url=reverse_lazy("donation_success")),
            status_listener=subscription_notification_listener,
            description_template="donations/subscription_description.html",
            description_context_generator=subscription_description_context_generator,
        )

        register_subscription_type(monthly_donation_subscription_type)

        ## CONTRIBUTIONS
        contribution_payment_type = PaymentType(
            self.CONTRIBUTION_TYPE,
            "Contribution financière volontaire",
            RedirectView.as_view(url=reverse_lazy("contribution_success")),
            status_listener=notification_listener,
            description_template="donations/description.html",
            description_context_generator=payment_description_context_generator,
            matomo_goal=settings.CONTRIBUTION_MATOMO_GOAL,
        )

        register_payment_type(contribution_payment_type)

        contribution_subscription_type = SubscriptionType(
            self.CONTRIBUTION_TYPE,
            "Contribution financière volontaire",
            RedirectView.as_view(url=reverse_lazy("contribution_success")),
            status_listener=subscription_notification_listener,
            description_template="donations/subscription_description.html",
            description_context_generator=subscription_description_context_generator,
            day_of_month=settings.CONTRIBUTION_DONATION_DAY,
        )

        register_subscription_type(contribution_subscription_type)
