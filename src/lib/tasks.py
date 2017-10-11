from celery import shared_task

from .geo import geocode_element
from events.models import Event
from groups.models import SupportGroup

__all__ = ['geocode_event', 'geocode_support_group']


def create_geocoder(model):
    def geocode_model(pk):
        try:
            item = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return

        if geocode_element(item):
            item.save()

    geocode_model.__name__ = "geocode_{}".format(model.__name__.lower())

    return shared_task(geocode_model)


geocode_event = create_geocoder(Event)
geocode_support_group = create_geocoder(SupportGroup)
