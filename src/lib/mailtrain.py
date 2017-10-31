from datetime import datetime
import requests
from requests import HTTPError

from api.settings import MAILTRAIN_HOST, MAILTRAIN_LIST_ID, MAILTRAIN_API_KEY


params = {'access_token': MAILTRAIN_API_KEY}

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
    try:
        response = requests.post(MAILTRAIN_HOST + '/api/subscribe/' + MAILTRAIN_LIST_ID, data=data, params=params, json=True)
        response.raise_for_status()
    except HTTPError as err:
        if response.status_code == 400:
            return False

        raise err

    return True


def unsubscribe(email):
    data = {
        'EMAIL': email
    }

    requests.post(MAILTRAIN_HOST + '/api/unsubscribe/' + MAILTRAIN_LIST_ID, data=data, params=params, json=True)\
        .raise_for_status()


def delete(email):
    data = {
        'EMAIL': email
    }

    response = None
    try:
        response = requests.post(MAILTRAIN_HOST + '/api/delete/' + MAILTRAIN_LIST_ID, data=data, params=params, json=True)
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



