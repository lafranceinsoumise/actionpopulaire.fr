from django.contrib.gis.db.models.functions import Distance
from django.core.management.base import BaseCommand

from agir.events.actions.notifications import new_event_suggestion_notification
from agir.people.models import Person
from agir.events.models import Event


class Command(BaseCommand):
    SUGGEST_LIMIT_METERS = 50000

    help = "suggest an event to each user"

    def handle(self, limit=SUGGEST_LIMIT_METERS, *args, **options):
        for person in Person.objects.all():
            base_queryset = Event.objects.with_serializer_prefetch(person)

            if person.coordinates is not None:
                near_event = (
                    base_queryset.upcoming()
                    .annotate(distance=Distance("coordinates", person.coordinates))
                    .filter(distance__lte=limit)
                    .order_by("?")
                    .first()
                )
                new_event_suggestion_notification(near_event, person)
