from datetime import datetime
from urllib3 import Retry
import requests
from requests import HTTPError

from django.conf import settings
from django.db.models import Q

from front.utils import generate_token_params
from urllib.parse import urlencode

params = {'access_token': settings.MAILTRAIN_API_KEY}


s = requests.Session()
a = requests.adapters.HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1))
b = requests.adapters.HTTPAdapter(max_retries=Retry(total=5, backoff_factor=1))
s.mount('https://', a)
s.mount('http://', b)


def data_from_person(person):
    data = {}

    is_animateur = Q(is_referent=True) | Q(is_manager=True)
    inscriptions = [
        ('evenements_yes' if person.events.upcoming().count() > 0 else 'evenements_no'),
        ('groupe_yes' if person.supportgroups.active().count() > 0 else 'groupe_no'),
        ('groupe_certifié_yes' if person.supportgroups.active().filter(subtypes__label=settings.CERTIFIED_GROUP_SUBTYPE).count() > 0 else 'groupe_certifié_no'),
        ('groupe_anim_yes' if person.memberships.active().filter(is_animateur).count() > 0 else 'groupe_anim_no'),
        ('groupe_certifié_anim_yes' if person.memberships.active().filter(is_animateur & Q(supportgroup__subtypes__label=settings.CERTIFIED_GROUP_SUBTYPE)).count() > 0 else 'groupe_certifié_anim_no'),
    ]

    data['FIRST_NAME'] = person.first_name
    data['LAST_NAME'] = person.last_name
    data['MERGE_ZIPCODE'] = person.location_zip
    data['MERGE_INSCRIPTIONS'] = ','.join(inscriptions)
    data['MERGE_LOGIN_QUERY'] = urlencode(generate_token_params(person))
    data['MERGE_TAGS'] = ',' + ','.join(t.label for t in person.tags.filter(exported=True)) + ','

    return data


def subscribe(email, fields=None):
    data = {
        'EMAIL': email,
        'FORCE_SUBSCRIBE': 'yes',
        'MERGE_API_UPDATED': datetime.utcnow(),
    }

    if fields is not None:
        data = {**data, **fields}

    response = None

    if settings.MAILTRAIN_DISABLE:
        return True

    try:
        response = s.post(settings.MAILTRAIN_HOST + '/api/subscribe/' + settings.MAILTRAIN_LIST_ID, data=data, params=params, json=True)
        response.raise_for_status()
    except HTTPError as err:
        if response.status_code == 400:
            return False

        raise err

    return True


def unsubscribe(email):
    data = {
        'EMAIL': email,
        'MERGE_API_UPDATED': datetime.utcnow(),
    }

    if settings.MAILTRAIN_DISABLE:
        return True

    s.post(settings.MAILTRAIN_HOST + '/api/unsubscribe/' + settings.MAILTRAIN_LIST_ID, data=data, params=params, json=True)\
        .raise_for_status()


def delete(email):
    data = {
        'EMAIL': email
    }

    response = None

    if settings.MAILTRAIN_DISABLE:
        return True

    try:
        response = s.post(settings.MAILTRAIN_HOST + '/api/delete/' + settings.MAILTRAIN_LIST_ID, data=data, params=params, json=True)
        response.raise_for_status()
    except HTTPError as err:
        if response is not None and response.status_code == 404:
            return False

        raise err

    return True


def update_person(person):
    data = data_from_person(person)
    emails = list(person.emails.all())

    for i, email in enumerate(emails):
        local_part, domain = email.address.rsplit('@', 1)
        if not email.bounced and domain.lower() not in settings.EMAIL_DISABLED_DOMAINS:
            primary_email = email
            other_emails = emails[:i] + emails[i+1:]
            break
    else:
        primary_email = None
        other_emails = emails

    if primary_email is not None:
        if person.subscribed:
            subscribe(primary_email.address, data)
        else:
            unsubscribe(primary_email.address)

    for email in other_emails:
        if not email.bounced:
            delete(email.address)


def delete_person(person):
    for email in person.emails.all():
        delete(email.address)
