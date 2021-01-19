import logging

import re
import requests
from data_france.models import CodePostal, Commune
from django.contrib.gis.geos import Point
from unidecode import unidecode

from .models import LocationMixin

logger = logging.getLogger(__name__)

NON_WORD = re.compile("[^\w]+")
MULTIPLE_SPACES = re.compile("\s\s+")

BAN_ENDPOINT = "https://api-adresse.data.gouv.fr/search"
NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/"


def normaliser_nom_ville(s):
    return MULTIPLE_SPACES.sub(" ", NON_WORD.sub(" ", unidecode(s.strip()))).lower()


def geocode_element(item):
    """Geocode an item in the background

    :param item:
    :return:
    """

    # geocoding only if got at least: country AND (city OR zip)
    if item.location_country and (item.location_city or item.location_zip):
        if item.location_country == "FR":
            geocode_france(item)
        else:
            geocode_internationally(item)
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


def geocode_data_france(item):
    if item.location_citycode:
        try:
            commune = Commune.objects.get(code=item.location_citycode)
        except Commune.MultipleObjectsReturned:
            commune = Commune.objects.get(
                code=item.location_citycode, type=Commune.TYPE_COMMUNE
            )
        except Commune.DoesNotExist:
            commune = None

        if commune is not None:
            item.coordinates = commune.geometry.centroid
            item.coordinates_type = (
                LocationMixin.COORDINATES_CITY
                if commune.type == Commune.TYPE_COMMUNE
                else LocationMixin.COORDINATES_DISTRICT
            )
            item.location_city = commune.nom_complet
            item.location_citycode = commune.code
            return

    if item.location_zip:
        try:
            code_postal = CodePostal.objects.get(code=item.location_zip)
        except CodePostal.DoesNotExist:
            pass
        else:
            nb_communes = code_postal.communes.count()

            if nb_communes == 1:
                commune = code_postal.communes.get()
                item.coordinates = commune.geometry.centroid
                item.coordinates_type = (
                    LocationMixin.COORDINATES_CITY
                    if commune.type == Commune.TYPE_COMMUNE
                    else LocationMixin.COORDINATES_DISTRICT
                )
                item.location_city = commune.nom_complet
                item.location_citycode = commune.code
                return

            if nb_communes > 1 and item.location_city:
                nom_normalise = normaliser_nom_ville(item.location_city)
                try:
                    commune = next(
                        v
                        for v in code_postal.communes.all()
                        if normaliser_nom_ville(v.nom) == nom_normalise
                    )
                    if commune.geometry:
                        item.coordinates = commune.geometry.centroid
                        item.location_citycode = commune.code
                        item.coordinates_type = (
                            LocationMixin.COORDINATES_CITY
                            if commune.type == Commune.TYPE_COMMUNE
                            else LocationMixin.COORDINATES_DISTRICT
                        )
                        return
                except StopIteration:
                    pass

            if nb_communes > 1:
                code_postal = CodePostal.objects.raw(
                    """
                    SELECT cp.*, ST_CENTROID(ST_UNION(c.geometry :: geometry)) centroid
                    FROM data_france_codepostal cp
                    JOIN data_france_codepostal_communes cc ON cp.id = cc.codepostal_id
                    JOIN data_france_commune c on cc.commune_id = c.id
                    WHERE cp.id = %(cp_id)s
                    GROUP BY cp.id; 
                """,
                    {"cp_id": code_postal.id},
                )[0]
                item.coordinates = code_postal.centroid
                item.coordinates_type = LocationMixin.COORDINATES_UNKNOWN_PRECISION
                return

    # pas de code postal
    if item.location_city:
        nom_normalise = normaliser_nom_ville(item.location_city)
        communes = [
            c
            for c in Commune.objects.search(item.location_city)
            if normaliser_nom_ville(c.nom_complet) == nom_normalise
        ]

        if len(communes) == 1:
            commune = communes[0]
            if commune.geometry is not None:
                item.coordinates = commune.geometry.centroid
                item.coordinates_type = (
                    LocationMixin.COORDINATES_CITY
                    if commune.type == Commune.TYPE_COMMUNE
                    else LocationMixin.COORDINATES_DISTRICT
                )
                item.location_city = commune.nom_complet
                item.location_citycode = commune.code
                return

    item.coordinates = None
    item.coordinates_type = LocationMixin.COORDINATES_NOT_FOUND


def geocode_france(item):
    """Trouver la localisation géographique d'un item

    Si on a juste un code postal ou une ville, on utilise les coordonnées données
    par data_france.

    Dans le cas où on a une adresse plus précise, on peut aller interroger la BAN.
    """

    has_precise_address = item.location_address1 or item.location_address2

    if not has_precise_address:
        geocode_data_france(item)
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


def geocode_internationally(item):
    """Find location of an item with its address for non French addresses

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
        res = requests.get(
            NOMINATIM_ENDPOINT,
            params=query,
            headers={
                "User-Agent": "La France insoumise events platform (if there is any problem with "
                "our usage please contact us at site@lafranceinsoumise.fr)"
            },
        )
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


def get_commune(item):
    commune = None
    if item.location_citycode:
        try:
            commune = Commune.objects.get(code=item.location_citycode)
        except Commune.MultipleObjectsReturned:
            commune = Commune.objects.get(
                code=item.location_citycode, type=Commune.TYPE_COMMUNE
            )
        except Commune.DoesNotExist:
            commune = None
    if item.location_zip:
        try:
            code_postal = CodePostal.objects.get(code=item.location_zip)
        except CodePostal.DoesNotExist:
            pass
        else:
            nb_communes = code_postal.communes.count()
            if nb_communes == 1:
                commune = code_postal.communes.get()
            if nb_communes > 1 and item.location_city:
                nom_normalise = normaliser_nom_ville(item.location_city)
                try:
                    commune = next(
                        v
                        for v in code_postal.communes.all()
                        if normaliser_nom_ville(v.nom) == nom_normalise
                    )
                except StopIteration:
                    pass
    if item.location_city:
        nom_normalise = normaliser_nom_ville(item.location_city)
        communes = [
            c
            for c in Commune.objects.search(item.location_city)
            if normaliser_nom_ville(c.nom_complet) == nom_normalise
        ]
        if len(communes) == 1:
            commune = communes[0]

    return commune
