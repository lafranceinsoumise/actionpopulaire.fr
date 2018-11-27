from django.core.management.base import BaseCommand
from django.db.models import Q

from agir.people.models import Person


class Command(BaseCommand):
    date_format = "%d/%m/%Y"

    help = "Statistics of numbers of rsvps for a draw to an event"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument("event_id", type=str)
        parser.add_argument("-t", "--tag", dest="tags", action="append", default=[])
        parser.add_argument(
            "--tags-contains", dest="tags_contains", type=str, default=None
        )
        parser.add_argument("-c", "--count-goal", dest="goal", type=int, default=None)

    def handle(self, event_id, tags, tags_contains, goal, **kwargs):
        binaries = (
            Person.objects.filter(draw_participation=True)
            .exclude(gender=Person.GENDER_OTHER)
            .count()
            / Person.objects.filter(draw_participation=True).count()
        )

        for g, label in Person.GENDER_CHOICES:
            tags_query = Q(tags__label__in=tags)
            if tags_contains is not None:
                tags_query = tags_query | Q(tags__label__contains=tags_contains)
            tas = Person.objects.filter(Q(gender=g) & tags_query).count()
            rsvp = Person.objects.filter(gender=g, events__id=event_id).count()
            print(f"{label} : ")
            print(f"{rsvp} inscrit⋅e⋅s sur {tas} TAS (taux {rsvp/tas})")

            if goal is not None:
                gender_goal = (
                    round(goal * binaries / 2)
                    if g != Person.GENDER_OTHER
                    else round(goal * (1 - binaries))
                )
                print(
                    f"Il faut tirer {round((gender_goal-rsvp)*(tas/rsvp))} pour atteindre {gender_goal}."
                )
