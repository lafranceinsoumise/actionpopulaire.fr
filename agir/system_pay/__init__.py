import dataclasses
import logging
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.urls import path
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..payments.abstract_payment_mode import AbstractPaymentMode

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class SystemPayConfig:
    site_id: str
    production: bool
    certificate: str
    currency: int = 978
    api_password: Optional[str] = None
    api_hmac_key: Optional[str] = None


class AbstractSystemPayPaymentMode(AbstractPaymentMode):
    can_retry = True
    can_cancel = True
    can_refund = True

    webhook_url = "webhook/"
    failure_url = "retour/<int:pk>/"
    api_notification_url = "api/notification/"

    id = None
    url_fragment = None
    label = "Par carte"
    category = "payment_card"

    sp_config: SystemPayConfig

    @cached_property
    def api_client(self):
        from agir.system_pay.rest_api import SystemPayRestAPI

        return SystemPayRestAPI(self.sp_config)

    @cached_property
    def payment_view(self):
        from . import views

        return views.SystempayRedirectView.as_view(sp_config=self.sp_config)

    @cached_property
    def retry_payment_view(self):
        from . import views

        return views.SystempayRedirectView.as_view(sp_config=self.sp_config)

    @cached_property
    def subscription_view(self):
        from . import views

        return views.SystemPaySubscriptionRedirectView.as_view(sp_config=self.sp_config)

    def cancel_or_refund_payment_action(self, payment, *args, comment="", **kwargs):
        from agir.system_pay.actions import update_payment_from_transaction
        from agir.system_pay.models import SystemPayTransaction

        sp_transaction = (
            payment.systempaytransaction_set.filter(
                status=SystemPayTransaction.STATUS_COMPLETED, uuid__isnull=False
            )
            .order_by("-created")
            .first()
        )

        if not sp_transaction or not sp_transaction.uuid:
            raise ValueError(
                "Aucune transaction SystemPay n'est associée à ce paiement"
            )

        try:
            is_refunded, answer = self.api_client.cancel_or_refund_transaction(
                sp_transaction, payment.price, comment=comment
            )
        except (ValueError, SystemPayError) as e:
            logger.error(
                f"Le {str(payment)} n'a pas pu être annulé/remboursé. {repr(e)}",
                exc_info=True,
            )
            raise

        sp_transaction.webhook_calls.append(answer)

        if is_refunded:
            sp_transaction.status = SystemPayTransaction.STATUS_REFUNDED
        else:
            sp_transaction.status = SystemPayTransaction.STATUS_CANCELED

        with transaction.atomic():
            sp_transaction.save(update_fields=["status", "webhook_calls"])
            update_payment_from_transaction(payment, sp_transaction)

    def subscription_terminate_action(self, subscription):
        sp_subscription = subscription.system_pay_subscriptions.get(active=True)
        alias = sp_subscription.alias
        self.api_client.cancel_alias(alias)
        alias.active = False
        alias.save(update_fields=["active"])
        sp_subscription.active = False
        sp_subscription.save(update_fields=["active"])

    def subscription_replace_action(self, previous_subscription, new_subscription):
        from agir.system_pay.models import SystemPaySubscription

        previous_sp_subscription = previous_subscription.system_pay_subscriptions.get(
            active=True
        )
        alias = previous_sp_subscription.alias

        self.api_client.cancel_subscription(previous_subscription)
        previous_sp_subscription.active = False
        previous_sp_subscription.save(update_fields=["active"])

        try:
            subscription_id = self.api_client.create_subscription(
                subscription=new_subscription, alias=alias
            )
        except SystemPayError:
            logger.error(
                f"Attention: lors du remplace de souscription, souscription {previous_subscription.pk} annulée"
                f" mais erreur lors de la création de la souscription {new_subscription.pk}."
            )
            raise

        SystemPaySubscription.objects.create(
            identifier=subscription_id,
            subscription=new_subscription,
            alias=alias,
            active=True,
        )

    def get_urls(self):
        from . import views

        return [
            path(
                self.webhook_url,
                views.SystemPayWebhookView.as_view(
                    sp_config=self.sp_config, mode_id=self.id
                ),
                name="webhook",
            ),
            path(self.failure_url, views.failure_view, name="failure"),
            path(
                self.api_notification_url,
                views.SystemPayRestAPINotificationView.as_view(
                    sp_config=self.sp_config, mode_id=self.id
                ),
                name="api_notification",
            ),
        ]


class SystemPayPaymentMode(AbstractSystemPayPaymentMode):
    id = "system_pay"
    url_fragment = "carte"
    label = _("Par carte bleue")
    title = "Paiement par carte bleue à l'AF LFI"

    sp_config = SystemPayConfig(
        site_id=settings.SYSTEMPAY_SITE_ID,
        production=settings.SYSTEMPAY_PRODUCTION,
        currency=settings.SYSTEMPAY_CURRENCY,
        certificate=settings.SYSTEMPAY_CERTIFICATE,
        api_password=settings.SYSTEMPAY_API_PASSWORD,
    )


class SystemPayError(Exception):
    def __init__(
        self, message, system_pay_code=None, detailed_message=None, response_data=None
    ):
        super().__init__(message, system_pay_code)
        self.message = message
        self.system_pay_code = system_pay_code
        self.detailed_message = detailed_message
        self.response_data = response_data

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"{self.__class__.__name__}({self.message!r}, system_pay_code={self.system_pay_code!r}, detailed_message={self.detailed_message!r})"
