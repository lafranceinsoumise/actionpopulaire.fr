from celery import shared_task

from . import geo
from events.models import Event
from groups.models import SupportGroup

__all__ = ['geocode_event', 'geocode_support_group']


def geocode_element(item):
    """Geocode an item in the background

    :param item:
    :return:
    """

    # geocoding only if got at least: city, country
    if item.location_city and item.location_country:
        if item.location_country == 'FR':
            geo.geocode_ban(item)
        else:
            geo.geocode_nominatim(item)


def create_geocoder(model):
    def geocode_model(pk):
        try:
            item = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return

        geocode_element(item)

    geocode_model.__name__ = "geocode_{}".format(model.__name__.lower())

    return shared_task(geocode_model)


geocode_event = create_geocoder(Event)
geocode_support_group = create_geocoder(SupportGroup)
