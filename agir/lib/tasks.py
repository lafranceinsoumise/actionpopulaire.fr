from django.contrib.gis.geos import Point
from django.db import IntegrityError
from agir.people.models import Person
from .celery import http_task
from .geo import geocode_element
from agir.carte.models import StaticMapImage

__all__ = ["geocode_person", "create_static_map_image_from_coordinates"]


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


@http_task
def create_static_map_image_from_coordinates(coordinates):
    center = Point(*coordinates)
    try:
        # Do not create image if one exists for a close enough point
        StaticMapImage.objects.get(
            center__dwithin=(center, StaticMapImage.UNIQUE_CENTER_MAX_DISTANCE)
        )
        return
    except StaticMapImage.MultipleObjectsReturned:
        return
    except StaticMapImage.DoesNotExist:
        pass

    try:
        StaticMapImage.objects.create_from_jawg(center=center)
    except IntegrityError:
        # Ignore error if image already exists for the given coordinates
        pass
