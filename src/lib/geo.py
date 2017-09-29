import requests
from django.contrib.gis.geos import Point

import logging
from .models import LocationMixin

logger = logging.getLogger(__name__)

BAN_ENDPOINT = 'https://api-adresse.data.gouv.fr/search'
NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/"


def geocode_ban(item):
    q = ' '.join(
        l for l in [item.location_address1, item.location_address2, item.location_zip, item.location_city] if l)

    query = {
        'q': q,
        'postcode': item.location_zip,
        'limit': 5
    }

    try:
        res = requests.get(BAN_ENDPOINT, params=query)
        res.raise_for_status()
        results = res.json()
    except requests.RequestException:
        logger.exception('Error while geocoding French address with BAN')
        return
    except ValueError:
        logger.exception('Invalid JSON while geocoding French address with BAN')
        return

    if 'features' not in results:
        logger.error('Incorrect result from BAN')
        return

    types = {
        'housenumber': LocationMixin.COORDINATES_EXACT,
        'street': LocationMixin.COORDINATES_STREET,
        'city': LocationMixin.COORDINATES_CITY
    }

    for feature in results['features']:
        if feature['geometry']['type'] != "Point":
            continue
        if feature['properties']['type'] in types:
            item.coordinates = Point(*feature['geometry']['coordinates'])
            item.coordinates_type = types[feature['properties']['type']]
            item.save()
            return

    item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND
    item.save()


def geocode_nominatim(item):
    q = ' '.join(l for l in [item.location_address1, item.location_address2, item.location_zip, item.location_city,
                             item.location_state] if l)

    query = {
        'format': 'json',
        'q': q,
        'limit': 1
    }

    if item.location_country:
        query['countrycodes'] = str(item.location_country)

    try:
        res = requests.get(NOMINATIM_ENDPOINT, params=query)
        res.raise_for_status()
        results = res.json()
    except requests.RequestException:
        logger.exception('Error while geocoding address with Nominatim')
        return
    except ValueError:
        logger.exception('Invalid JSON while geocoding address with Nominatim')
        return

    print(repr(results))

    if results:
        item.coordinates = Point(float(results[0]['lon']), float(results[0]['lat']))
        item.coordinates_type = LocationMixin.COORDINATES_UNKNOWN_PRECISION
    else:
        item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND

    item.save()
