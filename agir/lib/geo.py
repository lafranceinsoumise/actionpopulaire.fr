import json
import logging
from pathlib import Path

import requests
from django.contrib.gis.geos import Point

from .models import LocationMixin

logger = logging.getLogger(__name__)

BAN_ENDPOINT = "https://api-adresse.data.gouv.fr/search"
NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/"


with open(Path(__file__).parent / "data" / "arrondissements.json") as f:
    ARRONDISSEMENTS = json.load(f)


def geocode_element(item):
    """Geocode an item in the background

    :param item:
    :return:
    """

    # geocoding only if got at least: country AND (city OR zip)
    if item.location_country and (item.location_city or item.location_zip):
        if item.location_country == "FR":
            geocode_ban(item)
        else:
            geocode_nominatim(item)
    else:
        item.coordinates = None
        item.coordinates_type = LocationMixin.COORDINATES_NO_POSITION


def get_results_from_ban(query):
    try:
        res = requests.get(BAN_ENDPOINT, params=query, timeout=5)
        res.raise_for_status()
        results = res.json()
    except requests.RequestException:
        logger.warning(
            f"Network error while geocoding '{query!r}' with BAN", exc_info=True
        )
        raise
    except ValueError:
        logger.warning(
            f"Invalid JSON while geocoding '{query!r}' with BAN", exc_info=True
        )
        raise

    if "features" not in results:
        logger.warning(f"Incorrect result from BAN for address '{query!r}'")
        return None
    return results


def geocode_ban_district_exception(item):
    arrondissement = ARRONDISSEMENTS[item.location_zip]
    item.location_citycode = arrondissement["citycode"]
    item.coordinates = Point(*arrondissement["coordinates"])
    item.location_city = arrondissement["city"]
    item.coordinates_type = LocationMixin.COORDINATES_DISTRICT


def geocode_ban_citylevel(item):
    query = {
        "q": item.location_city or item.location_zip,
        "type": "municipality",
        "limit": 30,
    }
    if item.location_zip:
        query["postcode"] = item.location_zip

    results = get_results_from_ban(query)
    if not results:
        item.coordinates = None
        item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND
        return

    citycodes = [
        f["properties"]["citycode"]
        for f in results["features"]
        if f["geometry"]["type"] == "Point"
    ]
    coordinates = [
        f["geometry"]["coordinates"]
        for f in results["features"]
        if f["geometry"]["type"] == "Point"
    ]

    if len(coordinates) == 0:
        item.coordinates = None
        item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND
        return

    if item.location_city:
        # si on a un nom de ville, on prend le premier de la liste, ça devrait être le bon
        item.coordinates = Point(coordinates[0])
        item.location_citycode = citycodes[0]

    else:
        # sinon, on prend le milieu des différentes villes
        lon = sum(c[0] for c in coordinates) / len(coordinates)
        lat = sum(c[1] for c in coordinates) / len(coordinates)

        item.coordinates = Point(lon, lat)
        item.coordinates_type = (
            LocationMixin.COORDINATES_CITY
            if len(coordinates) == 1
            else LocationMixin.COORDINATES_UNKNOWN_PRECISION
        )
        item.location_citycode = citycodes[0] if len(set(citycodes)) == 1 else ""


def geocode_ban(item):
    """Find the location of an item using its location fields

    :param item:
    """

    no_address = not item.location_address1 and not item.location_address2

    if no_address:
        if item.location_zip in ARRONDISSEMENTS:
            geocode_ban_district_exception(item)
            return

        geocode_ban_citylevel(item)
        return

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
    results = get_results_from_ban(query)
    if results is None:
        # there has been a network error
        return

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
            item.location_citycode = feature["properties"]["citycode"]
            return

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
        raise
    except ValueError:
        logger.warning(
            f"Invalid JSON while geocoding address '{display_address}' with Nominatim",
            exc_info=True,
        )
        raise

    if results:
        item.coordinates = Point(float(results[0]["lon"]), float(results[0]["lat"]))
        item.coordinates_type = LocationMixin.COORDINATES_UNKNOWN_PRECISION
        return
    else:
        item.coordinates = None
        item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND
        return
