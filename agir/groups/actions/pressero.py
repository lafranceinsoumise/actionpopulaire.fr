import json
from secrets import token_urlsafe
from typing import Optional

import requests
from django.http import HttpResponseRedirect
from requests.auth import AuthBase
from django.conf import settings

from agir.people.models import Person


class PresseroAuthentication(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r: requests.Request):
        r.headers["Authorization"] = f"Token {self.token}"
        return r


PRESSERO_LOGIN = "person-{pk}"
PRESSERO_EMAIL = "person-{pk}@lafranceinsoumise.fr"


def is_pressero_enabled():
    return all(
        getattr(settings, a)
        for a in [
            "PRESSERO_API_URL",
            "PRESSERO_USER_NAME",
            "PRESSERO_SUBSCRIBER_ID",
            "PRESSERO_CONSUMER_ID",
            "PRESSERO_PASSWORD",
            "PRESSERO_SITE",
            "PRESSERO_APPROBATOR_ID",
            "PRESSERO_GROUP_ID",
        ]
    )


def authenticate_and_get_token(s: Optional[requests.Session] = None) -> str:
    if s is None:
        s = requests.Session()

    res = s.post(
        f"{settings.PRESSERO_API_URL}/V2/Authentication",
        json={
            "UserName": settings.PRESSERO_USER_NAME,
            "Password": settings.PRESSERO_PASSWORD,
            "SubscriberId": settings.PRESSERO_SUBSCRIBER_ID,
            "ConsumerId": settings.PRESSERO_CONSUMER_ID,
        },
    )
    res.raise_for_status()

    json = res.json()
    return json["Token"]


def create_user_for_person(
    person: Person, password: str, token: str, s: Optional[requests.Session] = None
):
    if s is None:
        s = requests.Session()

    payload = {
        "Email": PRESSERO_EMAIL.format(pk=person.pk),
        "FirstName": person.first_name or "??",
        "LastName": person.last_name or "??",
        "GroupIds": [settings.PRESSERO_GROUP_ID],
        "Culture": "fr-FR",
        "TZ": "Romance Standard Time",
        "Login": PRESSERO_LOGIN.format(pk=person.pk),
        "ReceiveNotifications": False,
        "ReceiveAllNotifications": False,
        "NewPassword": password,
        "MisId": str(person.pk),
        "UserSite": {
            "AddressBook": {
                "PreferredAddressId": None,
                "PreferredAddress": None,
                "Addresses": [],
            },
            "CanViewPricing": False,
            "IsTaxExempt": False,
            "TaxId": "",
            "CapturePurchaseOrder": 3,
        },
        "UserSiteCust": {
            "IsApproved": True,
            "IsShared": False,
            "ApprovalGroupId": settings.PRESSERO_APPROBATOR_ID,
        },
        "UserContactPermisssion": [
            {
                "group": "UserContactPermission",
                "type": "String",
                "optional": True,
                "field": "PrivacyPolicyAgreedOn",
                "description": "<p>The date when site user accepted the Privacy Policy.</p>",
            }
        ],
    }

    res = s.post(
        f"{settings.PRESSERO_API_URL}/site/{settings.PRESSERO_SITE}/users/?sendAccountCreationNotification=false",
        auth=PresseroAuthentication(token),
        json=payload,
    )

    res.raise_for_status()


def get_user_id_for_person(
    person: Person, token: str, s: requests.Session = None
) -> Optional[str]:
    if s is None:
        s = requests.Session()

    res = s.get(
        f"{settings.PRESSERO_API_URL}/site/{settings.PRESSERO_SITE}/users/",
        auth=PresseroAuthentication(token),
        params={
            "pageNumber": 0,
            "pageSize": 1,
            "includeDeleted": "true",
            "Login": PRESSERO_LOGIN.format(pk=person.pk),
        },
    )

    res.raise_for_status()

    payload = res.json()

    if not payload.get("Items"):
        return None

    else:
        return payload["Items"][0]["UserId"]


def update_user_password(
    user_id: str, new_password: str, token: str, s: requests.Session = None
):
    if s is None:
        s = requests.Session()

    res = s.put(
        f"{settings.PRESSERO_API_URL}/site/{settings.PRESSERO_SITE}/users/{user_id}",
        auth=PresseroAuthentication(token),
        json={
            "NewPassword": new_password,
            "UserSiteCust": {
                "IsApproved": True,
                "IsShared": False,
                "ApprovalGroupId": settings.PRESSERO_APPROBATOR_ID,
            },
        },
    )

    res.raise_for_status()


def redirect_to_pressero(person: Person):
    s = requests.Session()

    # 10 bytes for a temporary password should be more than enough
    password = token_urlsafe(10)

    token = authenticate_and_get_token(s)

    user_id = get_user_id_for_person(person, token, s)
    if user_id:
        update_user_password(user_id, password, token, s)
    else:
        create_user_for_person(person, password, token, s)

    return HttpResponseRedirect(
        f"https://{settings.PRESSERO_SITE}/login/?userEmail={PRESSERO_EMAIL.format(pk=person.pk)}&userPassword={password}"
    )
