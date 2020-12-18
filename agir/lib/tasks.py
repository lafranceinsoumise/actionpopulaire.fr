from agir.events.models import Event
from agir.groups.models import SupportGroup
from agir.people.models import Person
from .celery import http_task
from .geo import geocode_element

__all__ = ["geocode_event", "geocode_support_group", "geocode_person"]


def create_geocoder(model):
    def geocode_model(pk):
        try:
            item = model.objects.get(pk=pk)
        except model.DoesNotExist:
            return

        geocode_element(item)
        item.save()

    geocode_model.__name__ = "geocode_{}".format(model.__name__.lower())

    return http_task(geocode_model)


geocode_person = create_geocoder(Person)
