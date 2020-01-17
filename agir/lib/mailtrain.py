import warnings
from datetime import datetime
from urllib.parse import urlencode

import requests
import requests.adapters
from django.conf import settings
from django.db.models import Q
from requests import HTTPError
from urllib3 import Retry

from agir.lib.utils import generate_token_params

params = {"access_token": settings.MAILTRAIN_API_KEY}


s = requests.Session()
s.mount(
    "https://",
    requests.adapters.HTTPAdapter(
        max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[403, 504, 502])
    ),
)


def data_from_person(person, tmp_tags=None):
    data = {}

    is_animateur = Q(is_referent=True) | Q(is_manager=True)
    inscriptions = [
        ("evenements_yes" if person.events.upcoming().count() > 0 else "evenements_no"),
        ("groupe_yes" if person.supportgroups.active().count() > 0 else "groupe_no"),
        (
            "groupe_certifié_yes"
            if person.supportgroups.active().certified().count() > 0
            else "groupe_certifié_no"
        ),
        (
            "groupe_anim_yes"
            if person.memberships.active().filter(is_animateur).count() > 0
            else "groupe_anim_no"
        ),
        (
            "groupe_certifié_anim_yes"
            if person.memberships.active()
            .filter(
                is_animateur
                & Q(supportgroup__subtypes__label__in=settings.CERTIFIED_GROUP_SUBTYPES)
            )
            .count()
            > 0
            else "groupe_certifié_anim_no"
        ),
        (
            "country-{}".format(
                person.location_country if person.location_country else "FR"
            )
        ),
    ]

    data["FIRST_NAME"] = person.first_name
    data["LAST_NAME"] = person.last_name
    data["MERGE_GENDER"] = person.gender
    data["MERGE_ZIPCODE"] = (
        person.location_zip
        if (person.location_country == "FR" or not person.location_country)
        else str(person.location_country)
    )
    data["MERGE_INSCRIPTIONS"] = ",".join(inscriptions)
    data["MERGE_LOGIN_QUERY"] = urlencode(generate_token_params(person))
    data["MERGE_TAGS"] = (
        "," + ",".join(t.label for t in person.tags.filter(exported=True)) + ","
    )

    data["MERGE_REGION"] = " ".join([person.region, person.ancienne_region])
    data["MERGE_ANNEE_DE_NAISSANCE"] = (
        person.date_of_birth.year if person.date_of_birth else None
    )

    if tmp_tags:
        data["MERGE_TAGS"] = "," + ",".join(tmp_tags) + data["MERGE_TAGS"]

    if len(data["MERGE_TAGS"]) > 255:
        warnings.warn("Tag string is longer than 255 characters for " + person.email)

    return data


def subscribe_email(email, fields=None):
    data = {
        "EMAIL": email,
        "FORCE_SUBSCRIBE": "yes",
        "MERGE_API_UPDATED": datetime.utcnow(),
    }

    if fields is not None:
        data = {**data, **fields}

    response = None

    if settings.MAILTRAIN_DISABLE:
        return True

    try:
        response = s.post(
            settings.MAILTRAIN_HOST + "/api/subscribe/" + settings.MAILTRAIN_LIST_ID,
            data=data,
            params=params,
            json=True,
        )
        response.raise_for_status()
    except HTTPError as err:
        if response.status_code == 400:
            return False

        raise err

    return True


def unsubscribe_email(email):
    data = {"EMAIL": email, "MERGE_API_UPDATED": datetime.utcnow()}

    if settings.MAILTRAIN_DISABLE:
        return True

    try:
        s.post(
            settings.MAILTRAIN_HOST + "/api/unsubscribe/" + settings.MAILTRAIN_LIST_ID,
            data=data,
            params=params,
            json=True,
        ).raise_for_status()
    except requests.HTTPError as e:
        # if subscription did not exist, the status code will be 404: we don't want to fail in this situation
        if not hasattr(e, "response") or e.response.status_code != 404:
            raise


def delete_email(email):
    data = {"EMAIL": email}

    response = None

    if settings.MAILTRAIN_DISABLE:
        return True

    try:
        response = s.post(
            settings.MAILTRAIN_HOST + "/api/delete/" + settings.MAILTRAIN_LIST_ID,
            data=data,
            params=params,
            json=True,
        )
        response.raise_for_status()
    except HTTPError as err:
        if response is not None and response.status_code == 404:
            return False

        raise err

    return True


def update_person(person, tmp_tags=None):
    data = data_from_person(person, tmp_tags)
    emails = list(person.emails.all())

    for i, email in enumerate(emails):
        local_part, domain = email.address.rsplit("@", 1)
        if not email.bounced and domain.lower() not in settings.EMAIL_DISABLED_DOMAINS:
            primary_email = email
            other_emails = emails[:i] + emails[i + 1 :]
            break
    else:
        primary_email = None
        other_emails = emails

    if primary_email is not None:
        if person.subscribed and person.is_insoumise:
            subscribe_email(primary_email.address, data)
        else:
            unsubscribe_email(primary_email.address)

    for email in other_emails:
        delete_email(email.address)


def delete_person(person):
    for email in person.emails.all():
        delete_email(email.address)
