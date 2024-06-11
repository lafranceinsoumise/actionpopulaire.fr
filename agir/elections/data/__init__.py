import csv
from importlib.resources import open_text

import pandas as pd
from data_france.models import CirconscriptionLegislative, Commune
from django.contrib.gis.db.models import MultiPolygonField
from django.db.models.functions import Cast

campaign_managers_file = "campaign_managers.csv"

with open_text("agir.elections.data", campaign_managers_file) as file:
    campaign_managers = list(csv.DictReader(file))

campaign_managers_by_circo = {d["circo"]: d for d in campaign_managers}


def get_campaign_manager_for_circonscription_legislative(circonscription_legislative):
    """
    Function to retrieve the campaign manager data for a given CirconscriptionLegislative object
    :param circonscription_legislative:
    :return: a dictionnary with the campaign manager data or None
    """
    if not isinstance(circonscription_legislative, CirconscriptionLegislative):
        return None
    return campaign_managers_by_circo.get(circonscription_legislative.code, None)


def get_circonscription_legislative_for_commune(commune):
    """
    Function to retrieve a CirconscriptionLegislative instance for a given Commune object
    (NB: since a commune may have multiple circonscriptions, only the first match will be returned)
    :param commune:
    :return: a CirconscriptionLegislative instance or None
    """
    if commune.mairie_localisation is None:
        return None
    return (
        CirconscriptionLegislative.objects.filter(geometry__isnull=False)
        .filter(code__in=campaign_managers_by_circo.keys())
        .annotate(geo=Cast("geometry", output_field=MultiPolygonField(geography=False)))
        .filter(geo__contains=commune.mairie_localisation)
        .first()
    )


def get_campaign_manager_for_commune(commune):
    """
    Function to retrieve the campaign manager data for a given Commune object.
    (NB: since a commune may have multiple circonscriptions, only the first match will be returned)
    :param commune:
    :return: a dictionnary with the campaign manager data or None
    """
    if not isinstance(commune, Commune):
        return None
    circonscription_legislative = get_circonscription_legislative_for_commune(commune)
    if circonscription_legislative is None:
        return None
    return get_campaign_manager_for_circonscription_legislative(
        circonscription_legislative
    )


with open_text("agir.elections.data", "polling_stations.csv") as file:
    polling_station_dataframe = pd.read_csv(file, dtype=str).fillna("")
    polling_station_dataframe["code_commune"] = polling_station_dataframe[
        "code_commune"
    ].str.zfill(5)
    polling_station_dataframe["id"] = polling_station_dataframe["id_brut_insee"]
