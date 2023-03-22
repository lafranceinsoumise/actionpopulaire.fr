from django.apps import AppConfig
from django.conf import settings
from django.views.generic import RedirectView

from agir.payments.types import (
    register_payment_type,
    PaymentType,
    SubscriptionType,
    register_subscription_type,
)


class ILBAppConfig(AppConfig):
    name = "agir.ilb"
    verbose_name = "Institut La Boétie"

    SINGLE_TIME_DONATION_TYPE = "don_ilb"
    SUBSCRIPTION_TYPE = "don_regulier_ilb"

    def ready(self):
        from agir.donations.views.donations_views import notification_listener

        ilb_donation_type = PaymentType(
            self.SINGLE_TIME_DONATION_TYPE,
            "Don à l'Institut La Boétie",
            RedirectView.as_view(url=settings.ILB_DONS_REMERCIEMENTS),
            status_listener=notification_listener,
            description_template="ilb/dons/description.html",
            email_template_code="ILB_DONS_REMERCIEMENTS",
        )

        register_payment_type(ilb_donation_type)

        ilb_subscription_type = SubscriptionType(
            id=self.SUBSCRIPTION_TYPE,
            label="Don régulier à l'Institut la Boétie",
            success_view=RedirectView.as_view(url=settings.ILB_DONS_REMERCIEMENTS),
            status_listener=None,
            description_template="ilb/dons/description.html",
            day_of_month=12,
        )

        register_subscription_type(ilb_subscription_type)
