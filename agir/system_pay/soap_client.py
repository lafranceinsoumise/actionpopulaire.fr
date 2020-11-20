import uuid
from datetime import datetime

import hmac
from base64 import b64encode
from django.conf import settings
from django.utils import timezone
from django.utils.functional import cached_property
from zeep import Client, xsd

from agir.payments.models import Subscription
from agir.system_pay import SystemPayError
from agir.system_pay.utils import get_recurrence_rule

header_namespace = "{http://v5.ws.vads.lyra.com/Header/}"
prefix_namespace = "{http://v5.ws.vads.lyra.com/}"


class SystemPaySoapClient:
    def __init__(self, sp_config):
        self.sp_config = sp_config

    @cached_property
    def client(self):
        return Client("https://paiement.systempay.fr/vads-ws/v5?wsdl")

    @cached_property
    def cancel_subscription_type(self):
        return self.client.get_type(prefix_namespace + "cancelSubscription")

    @cached_property
    def common_request_type(self):
        return self.client.get_type(prefix_namespace + "commonRequest")

    @cached_property
    def query_request_type(self):
        return self.client.get_type(prefix_namespace + "queryRequest")

    @cached_property
    def order_request_type(self):
        return self.client.get_type(prefix_namespace + "orderRequest")

    @cached_property
    def card_request_type(self):
        return self.client.get_type(prefix_namespace + "cardRequest")

    @cached_property
    def subscription_request_type(self):
        return self.client.get_type(prefix_namespace + "subscriptionRequest")

    def _get_header(self):
        headers = list()
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
        elements = {
            "shopId": self.sp_config["site_id"],
            "requestId": request_id,
            "timestamp": timestamp,
            "mode": "PRODUCTION" if self.sp_config["production"] else "TEST",
            "authToken": b64encode(
                hmac.digest(
                    self.sp_config["certificate"].encode(),
                    (request_id + timestamp).encode(),
                    "sha256",
                )
            ).decode(),
        }

        for elem in elements:
            header = xsd.ComplexType(
                [xsd.Element(header_namespace + elem, xsd.String())]
            )
            headers.append(header(**{elem: elements[elem]}))

        return headers

    def cancel_alias(self, alias):
        res = self.client.service.cancelToken(
            _soapheaders=self._get_header(),
            commonRequest=self.common_request_type(),
            queryRequest=self.query_request_type(paymentToken=alias.identifier.hex),
        )

        if res["commonResponse"]["responseCode"] > 0:
            raise SystemPayError(res["commonResponse"]["responseCodeDetail"])

    def cancel_subscription(self, subscription):
        system_pay_subscription = subscription.system_pay_subscriptions.get(active=True)
        alias = system_pay_subscription.alias

        res = self.client.service.cancelSubscription(
            _soapheaders=self._get_header(),
            commonRequest=self.common_request_type(),
            queryRequest=self.query_request_type(
                paymentToken=alias.identifier.hex,
                subscriptionId=system_pay_subscription.identifier,
            ),
        )

        if res["commonResponse"]["responseCode"] > 0:
            raise SystemPayError(
                res["commonResponse"]["responseCodeDetail"],
                system_pay_code=res["commonResponse"]["responseCode"],
            )

    def get_subscription_details(self, subscription):
        system_pay_subscription = subscription.system_pay_subscriptions.get(active=True)
        alias = system_pay_subscription.alias

        res = self.client.service.getSubscriptionDetails(
            _soapheaders=self._get_header(),
            queryRequest=self.query_request_type(
                paymentToken=alias.identifier.hex,
                subscriptionId=system_pay_subscription.identifier,
            ),
        )

        if res["commonResponse"]["responseCode"] > 0:
            raise SystemPayError(
                res["commonResponse"]["responseCodeDetail"],
                system_pay_code=res["commonResponse"]["responseCode"],
            )

        return {
            "orderId": res["orderResponse"]["orderId"],
            **res["subscriptionResponse"],
        }

    def create_subscription(self, subscription, alias):
        """
        Crée une souscription côté SystemPay et renvoie l'identifiant de souscription
        SystemPay correspondant
        :param subscription: L'objet souscription pour lequel il faut créer la souscription
        :param alias: L'alias pour lequel il faut créer cette souscription
        :return: L'identifiant de souscription côté SystemPay
        """
        if subscription.status != Subscription.STATUS_WAITING:
            raise ValueError("La souscription doit être en attente.")

        if not alias.active:
            raise ValueError("L'alias doit être actif.")

        res = self.client.service.createSubscription(
            _soapheaders=self._get_header(),
            commonRequest=self.common_request_type(),
            orderRequest=self.order_request_type(orderId=f"S{subscription.id}"),
            subscriptionRequest=self.subscription_request_type(
                effectDate=(timezone.now() + timezone.timedelta(hours=2)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                ),
                amount=subscription.price,
                initialAmount=0,
                initialAmountNumber=0,
                currency=settings.SYSTEMPAY_CURRENCY,
                rrule=get_recurrence_rule(subscription),
            ),
            cardRequest=self.card_request_type(paymentToken=alias.identifier.hex),
        )

        if res["commonResponse"]["responseCode"] > 0:
            raise SystemPayError(
                res["commonResponse"]["responseCodeDetail"],
                system_pay_code=res["commonResponse"]["responseCode"],
            )

        return res["subscriptionResponse"]["subscriptionId"]
