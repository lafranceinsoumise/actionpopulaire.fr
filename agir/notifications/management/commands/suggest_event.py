from django.contrib.gis.db.models.functions import Distance
from django.core.management.base import BaseCommand
from django.utils import timezone
from tqdm import tqdm

from agir.activity.models import Activity
from agir.events.actions.notifications import new_event_suggestion_notification
from agir.events.models import Event
from agir.lib.management_utils import segment_argument
from agir.people.models import Person


class Command(BaseCommand):
    SUGGEST_LIMIT_METERS = 50000

    help = "suggest an event to each user"

    def add_arguments(self, parser):
        parser.add_argument("-S", "--segment", type=segment_argument)

    def handle(self, segment, limit=SUGGEST_LIMIT_METERS, *args, **options):
        if segment:
            person_queryset = segment.get_subscribers_queryset()
        else:
            person_queryset = Person.objects.all()

        person_queryset = (
            person_queryset.exclude(coordinates=None)
            .filter(
                role__is_active=True,
                role__last_login__gt=timezone.now() - timezone.timedelta(days=60),
            )  # seulement les gens s'étant déjà connectés dans les 2 derniers mois
            .exclude(
                activities__in=Activity.objects.filter(
                    type=Activity.TYPE_EVENT_SUGGESTION,
                    created__gt=timezone.now() - timezone.timedelta(hours=18),
                )
            )  # exclure les personnes ayant déjà reçu une suggestion aujourd'hui
        )

        pbar = tqdm(total=person_queryset.count())
        for person in person_queryset.iterator():
            base_queryset = (
                Event.objects.with_serializer_prefetch(person)
                .listed()
                .upcoming()
                .exclude(coordinates=None)
            )

            near_event = (
                base_queryset.annotate(
                    distance=Distance("coordinates", person.coordinates)
                )
                .filter(distance__lte=limit)
                .filter(start_time__lt=timezone.now() + timezone.timedelta(days=7))
                .exclude(attendees=person)
                .distinct()
                .order_by("distance")
                .first()
            )

            if near_event is not None:
                new_event_suggestion_notification(near_event, person)
                # Avoid sending event suggestions via email until stricter rules are defined
                # send_event_suggestion_email.delay(near_event.pk, person.pk)

            pbar.update()
        pbar.close()
