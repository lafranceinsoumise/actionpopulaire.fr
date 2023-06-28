import csv
import datetime
import json
from enum import Enum

import requests
from django.conf import settings

from agir.lib.sms.common import SMSSendException, SMSException

# API DOC : https://assistance.utilisateur-relationclient.sfrbusiness.fr/dmc/
#         :https://www.dmc.sfr-sh.fr/ApiWorkshop/doc/DMCv1_SFD064-API-Declenchement_a_distance.pdf

BULK_GROUP_SIZE = 100


class DMCBufferWSMedia(Enum):
    SMS = "SMS"


class DmcBufferError(Enum):
    AUTHENTICATION_FAILED = "KO<authentication_failed:{null}>"
    EMPTY_DMC_SERVICE_NAME = "KO<empty_dmcServiceName:{dmcServiceName vide}>"
    INVALID_JSON = "KO<Invalid JSON:{null}>"


class DmcBufferWS:
    BASE_URL = "https://www.dmc.sfr-sh.fr/DmcBufferWS/BufferMsg"
    TEMPLATE = {
        "transactional": "{message}",
        "marketing": "{message}\n\nSTOP au <#shortcode#>",
    }
    DEFAULT_TEMPLATE = TEMPLATE["marketing"]

    def __init__(self, sender=None, template=None):
        self.sender = sender if sender else settings.SFR_DEFAULT_SENDER
        self.template = self.TEMPLATE.get(template, self.DEFAULT_TEMPLATE)
        self.authentication = {
            "serviceId": settings.SFR_SERVICE_ID,
            "servicePassword": settings.SFR_PASSWORD,
            "spaceId": settings.SFR_SPACE_ID,
        }

    def _make_request(self, endpoint, data):
        data.update(self.authentication)
        response = requests.get(
            f"{self.BASE_URL}/{endpoint}",
            params=data,
        )
        return response

    def retrieve_sms(self, idSince=None, dSince=None):
        if dSince is None:
            dSince = datetime.datetime.now().timestamp()

        try:
            response = self._make_request(
                "getSingleCallCra", {"dSince": dSince, "idSince": idSince}
            )
        except Exception as e:
            raise SMSException(str(e))

        response = csv.DictReader(response.text, delimiter=";")
        response = {item["ID"]: item for item in response}

        return response

    def send_sms(
        self,
        message,
        recipient,
    ):
        data = {
            "messageUnitaire": json.dumps(
                {
                    "media": DMCBufferWSMedia.SMS.value,
                    "from": self.sender,
                    "address": recipient.as_national,
                    "msgContent": self.template.format(message=message),
                }
            )
        }

        try:
            response = self._make_request("addSingleCall", data)
        except Exception as e:
            raise SMSSendException(
                str(e),
                invalid=[recipient],
            )

        if not response or response.text.startswith("KO"):
            raise SMSSendException(
                f"L'API SFR a rencontré une erreur {response.text if response else ''}",
                invalid=[recipient],
            )

        # TODO: (maybe) check if the sms has actually been sent
        # cf.https://assistance.utilisateur-relationclient.sfrbusiness.fr/dmc/dmc-api-utilisation-de-dmcbufferws-json-2/

        return True


def send_sms(message, recipients, *, sender=None, template=None, **_):
    api_client = DmcBufferWS(sender, template)

    sent = set()
    not_sent = set()

    for recipient in recipients:
        ok = api_client.send_sms(message, recipient)
        sent.add(recipient.as_e164) if ok else not_sent.add(recipient.as_e164)

    return sent, not_sent
