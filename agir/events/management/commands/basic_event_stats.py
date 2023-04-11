import logging

from django.core.management.base import BaseCommand, CommandError

from agir.events.models import Event

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Display some statistics about one or more events"

    def add_arguments(self, parser):
        parser.add_argument("-i", "--ids", nargs="+", type=str)

    def handle(self, *args, **options):
        events_ids = options["ids"]

        message = "Bonjour,\n"
        if events_ids:
            events = Event.objects.filter(pk__in=events_ids)
            for event in events:
                message += f"Pour l'événement <b>{event.name} il y a {event.participants} participants, dont {event.participants_confirmes} confirmés</b>\n"

            message += "Bonne journée\n"
            self.stdout.write(message)
        else:
            raise CommandError("You must specify at least one event id")
