from django.apps import AppConfig
from django.conf import settings


class Presidentielle2022Config(AppConfig):
    name = "agir.presidentielle2022"

    DONATION_PAYMENT_TYPE = "don_2022"
    DONATION_SUBSCRIPTION_TYPE = "don_mensuel_2022"

    def ready(self):
        from agir.payments.types import (
            register_payment_type,
            PaymentType,
            register_subscription_type,
            SubscriptionType,
        )
        from django.views.generic import RedirectView
        from agir.donations.views import (
            notification_listener,
            subscription_notification_listener,
        )

        register_payment_type(
            PaymentType(
                id=self.DONATION_PAYMENT_TYPE,
                label="Don pour la campagne présidentielle",
                success_view=RedirectView.as_view(
                    url="https://melenchon2022.fr/don/merci/"
                ),
                status_listener=notification_listener,
                description_template="presidentielle2022/donations/description.html",
                email_template_code="DONATION_MESSAGE_2022",
                email_from=settings.EMAIL_FROM_MELENCHON_2022,
            )
        )

        register_payment_type(
            PaymentType(
                id=self.DONATION_SUBSCRIPTION_TYPE,
                label="Don automatique",
                success_view=RedirectView.as_view(
                    url="https://melenchon2022.fr/don/merci/"
                ),
                status_listener=notification_listener,
                description_template="presidentielle2022/donations/description.html",
                matomo_goal=settings.MONTHLY_DONATION_MATOMO_GOAL,
                email_template_code="DONATION_MESSAGE_2022",
                email_from=settings.EMAIL_FROM_MELENCHON_2022,
            )
        )

        subscription_type = SubscriptionType(
            self.DONATION_SUBSCRIPTION_TYPE,
            "Don mensuel",
            RedirectView.as_view(url="https://melenchon2022.fr/don/merci/"),
            status_listener=subscription_notification_listener,
            description_template="presidentielle2022/donations/subscription_description.html",
        )

        register_subscription_type(subscription_type)
