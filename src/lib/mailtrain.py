from datetime import datetime
import requests
from requests import HTTPError

from django.conf import settings

from front.utils import generate_token_params
from urllib.parse import urlencode

params = {'access_token': settings.MAILTRAIN_API_KEY}


def data_from_person(person):
    data = {}

    inscriptions = [
        ('evenements' if person.events.count() > 0 else 'sans_evenements'),
        ('groupe_appui' if person.supportgroups.count() > 0 else 'sans_groupe_appui')
    ]

    data['FIRST_NAME'] = person.first_name
    data['LAST_NAME'] = person.last_name
    data['MERGE_ZIPCODE'] = person.location_zip
    data['MERGE_INSCRIPTIONS'] = ','.join(inscriptions)
    data['MERGE_LOGIN_QUERY'] = urlencode(generate_token_params(person))

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
        response = requests.post(settings.MAILTRAIN_HOST + '/api/subscribe/' + settings.MAILTRAIN_LIST_ID, data=data, params=params, json=True)
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

    requests.post(settings.MAILTRAIN_HOST + '/api/unsubscribe/' + settings.MAILTRAIN_LIST_ID, data=data, params=params, json=True)\
        .raise_for_status()


def delete(email):
    data = {
        'EMAIL': email
    }

    response = None

    if settings.MAILTRAIN_DISABLE:
        return True

    try:
        response = requests.post(settings.MAILTRAIN_HOST + '/api/delete/' + settings.MAILTRAIN_LIST_ID, data=data, params=params, json=True)
        response.raise_for_status()
    except HTTPError as err:
        if response is not None and response.status_code == 404:
            return False

        raise err

    return True


def update_person(person):
    data = data_from_person(person)
    emails = list(person.emails.all())

    primary_email = emails[0]
    other_emails = emails[1:]

    if not primary_email.bounced:
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
