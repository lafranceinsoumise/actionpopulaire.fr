import requests
from celery import shared_task

from .geo import geocode_element
from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.people.models import Person

__all__ = ["geocode_event", "geocode_support_group", "geocode_person"]


def create_geocoder(model):
    def geocode_model(self, pk):
        try:
            item = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return

        try:
            geocode_element(item)
            item.save()
        except (ValueError, requests.RequestException) as exc:
            self.retry(countdown=60, exc=exc)

    geocode_model.__name__ = "geocode_{}".format(model.__name__.lower())

    return shared_task(geocode_model, bind=True)


geocode_event = create_geocoder(Event)
geocode_support_group = create_geocoder(SupportGroup)
geocode_person = create_geocoder(Person)
