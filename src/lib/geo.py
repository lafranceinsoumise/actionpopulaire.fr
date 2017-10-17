import requests
from django.contrib.gis.geos import Point

import logging
from .models import LocationMixin

logger = logging.getLogger(__name__)

BAN_ENDPOINT = 'https://api-adresse.data.gouv.fr/search'
NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/"


def geocode_element(item):
    """Geocode an item in the background

    :param item:
    :return:
    """

    # geocoding only if got at least: city, country
    if item.location_city and item.location_country:
        if item.location_country == 'FR':
            return geocode_ban(item)
        else:
            return geocode_nominatim(item)
    else:
        item.coordinates = None
        item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND


def geocode_ban(item):
    """Find the location of an item using its location fields

    :param item:
    :return: True if the item has changed (and should be saved), False in the other case
    """
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
        return False
    except ValueError:
        logger.exception('Invalid JSON while geocoding French address with BAN')
        return False

    if 'features' not in results:
        logger.error('Incorrect result from BAN')
        return False

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
            return True

    item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND


def geocode_nominatim(item):
    """Find location of an item with its address

    :return: True if the item has changed (and should be saved), False in the other case
    """
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
        return False
    except ValueError:
        logger.exception('Invalid JSON while geocoding address with Nominatim')
        return False

    print(repr(results))

    if results:
        item.coordinates = Point(float(results[0]['lon']), float(results[0]['lat']))
        item.coordinates_type = LocationMixin.COORDINATES_UNKNOWN_PRECISION
        return True
    else:
        item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND
        return True
