import hmac
import uuid
from datetime import datetime

from base64 import b64encode
from zeep import Client, xsd

from agir.system_pay import SystemPayError
from agir.system_pay.models import SystemPayTransaction

client = Client("https://paiement.systempay.fr/vads-ws/v5?wsdl")
header_namespace = "{http://v5.ws.vads.lyra.com/Header/}"
prefix_namespace = "{http://v5.ws.vads.lyra.com/}"
cancel_subscription_type = client.get_type(prefix_namespace + "cancelSubscription")
common_request_type = client.get_type(prefix_namespace + "commonRequest")
query_request_type = client.get_type(prefix_namespace + "queryRequest")


class SystemPaySoapClient:
    def __init__(self, sp_config):
        self.sp_config = sp_config

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

    def cancel_subscription(self, subscription):
        transaction = SystemPayTransaction.objects.get(
            subscription=subscription, status=SystemPayTransaction.STATUS_COMPLETED
        )
        res = client.service.cancelToken(
            _soapheaders=self._get_header(),
            commonRequest=common_request_type(),
            queryRequest=query_request_type(
                paymentToken=transaction.alias.identifier.hex
            ),
        )

        if res["commonResponse"]["responseCode"] > 0:
            raise SystemPayError(res["commonResponse"]["responseCodeDetail"])
