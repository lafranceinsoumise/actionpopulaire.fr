import json
import logging

import requests
from django.conf import settings
from requests import JSONDecodeError
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)


class MaterielRestAPIError(Exception):
    def __init__(self, message, res, extra_data=None):
        super().__init__(message, res.status_code)
        self.message = message
        self.extra_data = extra_data
        self.res = res
        try:
            data = res.json()
        except JSONDecodeError:
            pass
        else:
            self.message = data["message"]
            self.error_code = data["code"]
            self.extra_data = json.dumps(data["data"])

    def __str__(self):
        if self.error_code:
            return f"{self.message} ({self.error_code})"
        return self.message

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.message!r}, "
            f"status={self.res.status_code!r}, "
            f"extra_data={self.extra_data!r})"
        )


class MaterielRestAPI:
    BASE_URL = "https://materiel.actionpopulaire.fr/wp-json/wc/v3/"

    def __init__(self):
        self.session = requests.session()
        self.session.auth = HTTPBasicAuth(
            username=settings.MATERIEL_REST_API_USERNAME,
            password=settings.MATERIEL_REST_API_PASSWORD,
        )
        self.session.headers["Content-Type"] = "application/json"

    def _make_request(self, endpoint, params=None):
        if isinstance(params, dict):
            params = {key: value for key, value in params.items() if value is not None}
        res = self.session.get(f"{self.BASE_URL}{endpoint}", params=params)

        if res.status_code != 200:
            raise MaterielRestAPIError(f"L'API REST a renvoyé une erreur", res)

        try:
            data = res.json()
        except JSONDecodeError:
            raise MaterielRestAPIError(
                f"La réponse de l'API REST n'est pas au format JSON", res
            )

        return data

    def retrieve_sales_report(self, period=None, date_min=None, date_max=None):
        if date_min is not None:
            date_min = date_min.strftime("%Y-%m-%d")

        if date_max is not None:
            date_max = date_max.strftime("%Y-%m-%d")

        params = {
            "period": period,
            "date_min": date_min,
            "date_max": date_max,
        }

        sales_report = self._make_request("reports/sales", params=params)

        return sales_report[0]
