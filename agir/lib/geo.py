import re
import requests
from django.contrib.gis.geos import Point
from django.core.cache import cache

import logging
from .models import LocationMixin

logger = logging.getLogger(__name__)

BAN_ENDPOINT = "https://api-adresse.data.gouv.fr/search"
NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/"


def geocode_element(item):
    """Geocode an item in the background

    :param item:
    :return:
    """

    # geocoding only if got at least: city, country
    if item.location_city and item.location_country:
        if item.location_country == "FR":
            geocode_ban(item)
        else:
            geocode_nominatim(item)
    else:
        item.coordinates = None
        item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND


def geocode_ban(item):
    """Find the location of an item using its location fields

    :param item:
    :return: True if the item has changed (and should be saved), False in the other case
    """
    q = " ".join(
        l
        for l in [
            item.location_address1,
            item.location_address2,
            item.location_zip,
            item.location_city,
        ]
        if l
    )

    query = {"q": q, "postcode": item.location_zip, "limit": 5}

    display_address = f"{q} ({item.location_zip})"

    try:
        res = requests.get(BAN_ENDPOINT, params=query)
        res.raise_for_status()
        results = res.json()
    except requests.RequestException:
        logger.warning(
            f"Error while geocoding French address '{display_address}' with BAN",
            exc_info=True,
        )
        return False
    except ValueError:
        logger.warning(
            "Invalid JSON while geocoding French address '{display_address}' with BAN",
            exc_info=True,
        )
        return False

    if "features" not in results:
        logger.warning(f"Incorrect result from BAN for address '{display_address}'")
        return False

    types = {
        "housenumber": LocationMixin.COORDINATES_EXACT,
        "street": LocationMixin.COORDINATES_STREET,
        "city": LocationMixin.COORDINATES_CITY,
    }

    for feature in results["features"]:
        if feature["geometry"]["type"] != "Point":
            continue
        if feature["properties"]["type"] in types:
            item.coordinates = Point(*feature["geometry"]["coordinates"])
            item.coordinates_type = types[feature["properties"]["type"]]
            return True

    item.coordinates = None
    item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND


def geocode_nominatim(item):
    """Find location of an item with its address

    :return: True if the item has changed (and should be saved), False in the other case
    """
    q = " ".join(
        l
        for l in [
            item.location_address1,
            item.location_address2,
            item.location_zip,
            item.location_city,
            item.location_state,
        ]
        if l
    )

    query = {"format": "json", "q": q, "limit": 1}

    if item.location_country:
        query["countrycodes"] = str(item.location_country)

    display_address = f"{q} ({item.location_country})"

    try:
        res = requests.get(NOMINATIM_ENDPOINT, params=query)
        res.raise_for_status()
        results = res.json()
    except requests.RequestException:
        logger.warning(
            f"Error while geocoding address '{display_address}' with Nominatim",
            exc_info=True,
        )
        return False
    except ValueError:
        logger.warning(
            f"Invalid JSON while geocoding address '{display_address}' with Nominatim",
            exc_info=True,
        )
        return False

    if results:
        item.coordinates = Point(float(results[0]["lon"]), float(results[0]["lat"]))
        item.coordinates_type = LocationMixin.COORDINATES_UNKNOWN_PRECISION
        return True
    else:
        item.coordinates = None
        item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND
        return True
