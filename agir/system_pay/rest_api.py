import logging
from enum import Enum
from datetime import datetime
from typing import Any, Optional

import pydantic
import requests
from django.utils import timezone
from pydantic import BaseModel, constr
from requests import JSONDecodeError
from requests.auth import HTTPBasicAuth

from agir.payments.models import Subscription
from agir.system_pay import SystemPayConfig, SystemPayError
from agir.system_pay.models import SystemPaySubscription
from agir.system_pay.utils import get_recurrence_rule

logger = logging.getLogger(__name__)


class SystemPayAPIError(SystemPayError):
    """Signale une défaillance de l'API REST SystemPay"""

    def __repr__(self):
        return f"{self.__class__.__name__}(message={self.message!r})"


class APIStatus(Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"


class APIErrorCode(Enum):

    MISSING_ALIAS = "INT_030"
    UNKNOWN_ALIAS = "PSP_030"
    UNKNOWN_SUBSCRIPTION = "PSP_032"
    INVALID_SUBSCRIPTION = "PSP_033"


class CancelSuscriptionResponseCode(Enum):
    SUCCESS = 0
    ALIAS_UNKNOWN = 30
    SUBSCRIPTION_UNKNOWN = 32
    ERROR_UNKNOWN = 99


class APIResponse(BaseModel):
    status: APIStatus
    answer: Optional[Any]


class APIError(BaseModel):
    errorCode: str
    errorMessage: str
    detailedErrorCode: Optional[str]
    detailedErrorMessage: Optional[str]


class SubscriptionDetails(BaseModel):
    subscriptionId: constr(max_length=64)
    paymentMethodToken: Optional[constr(max_length=50)]
    orderId: constr(max_length=64)
    metadata: Optional[dict[str, Any]]
    effectDate: Optional[datetime]
    cancelDate: Optional[datetime]
    initialAmount: Optional[int]
    initialAmountNumber: Optional[int]
    amount: Optional[int]
    currency: Optional[constr(min_length=3, max_length=3)]
    pastPaymentsNumber: Optional[int]
    totalPaymentsNumber: Optional[int]
    rrule: Optional[constr(max_length=255)]
    description: Optional[constr(max_length=255)]


class SystemPayRestAPI:
    BASE_URL = "https://api.systempay.fr/api-payment/V4/"

    def __init__(self, sp_config: SystemPayConfig):
        self.sp_config = sp_config
        self.session = requests.session()
        self.session.auth = HTTPBasicAuth(
            username=sp_config.site_id,
            password=sp_config.api_password,
        )
        self.session.headers["Content-Type"] = "application/json"

    def _raise_error(self, answer):
        try:
            error = APIError.parse_obj(answer)
        except pydantic.ValidationError:
            raise SystemPayAPIError("Format du message d'erreur incorrect")

        raise SystemPayError(
            message=error.errorMessage,
            system_pay_code=error.errorCode,
            detailed_message=error.detailedErrorMessage,
        )

    def _make_request(self, endpoint, data):
        res = self.session.post(f"{self.BASE_URL}{endpoint}", json=data)

        if res.status_code != 200:
            raise SystemPayAPIError(
                f"L'API REST a renvoyé un status de message = {res.status_code!r}"
            )

        try:
            data = res.json()
        except JSONDecodeError:
            raise SystemPayAPIError(
                f"L'API REST n'a pas renvoyé de JSON = {res.content!r}"
            )

        try:
            message = APIResponse.parse_obj(data)
        except pydantic.ValidationError:
            raise SystemPayAPIError(
                f"L'API REST a renvoyé un format de message incorrect = {data!r}"
            )

        if message.status == APIStatus.ERROR:
            self._raise_error(message.answer)

        return message.answer

    def cancel_alias(self, alias):
        answer = self._make_request(
            "Token/Cancel", data={"paymentMethodToken": alias.identifier}
        )
        if not answer["responseCode"] == 0:
            raise SystemPayError(
                message=f"Impossible d'annuler l'alias de carte {alias!r}",
                system_pay_code=answer["responseCode"],
            )

    def cancel_subscription(self, subscription, termination_date=None):
        system_pay_subscription = subscription.system_pay_subscriptions.get(active=True)
        alias = system_pay_subscription.alias

        answer = self._make_request(
            "Subscription/Cancel",
            data={
                "paymentMethodToken": alias.identifier,
                "subscriptionId": system_pay_subscription.identifier,
                "terminationDate": termination_date.isoformat(),
            },
        )
        if not answer["responseCode"] == 0:
            raise SystemPayError(
                message=f"Impossible d'annuler la souscription {subscription!r}",
                system_pay_code=answer["responseCode"],
            )

    def get_subscription_details(self, subscription):
        system_pay_subscription: SystemPaySubscription = (
            subscription.system_pay_subscriptions.get(active=True)
        )
        alias = system_pay_subscription.alias

        answer = self._make_request(
            "Subscription/Get",
            data={
                "paymentMethodToken": alias.identifier,
                "subscriptionId": system_pay_subscription.identifier,
            },
        )

        try:
            subscription_details = SubscriptionDetails.parse_obj(answer)
        except pydantic.ValidationError:
            logger.error(f"Format incorrect d'une souscription systempay: {answer!r}")
            raise SystemPayAPIError("Format de l'objet renvoyé incorrect")

        return subscription_details

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

        answer = self._make_request(
            "Charge/CreateSubscription",
            data={
                "paymentMethodToken": alias.identifier,
                "amount": subscription.price,
                "currency": self.sp_config.currency,
                "effectDate": timezone.now().isoformat(),
                "rrule": get_recurrence_rule(subscription),
                # "installmentNumber": count_installments(subscription),  # ça fait pas doublon avec la rrule ?
            },
        )

        return answer["subcriptionId"]
