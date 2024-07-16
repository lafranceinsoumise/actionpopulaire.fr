import logging
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from agir.events.models import Event, RSVP

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
                amount = sum(
                    RSVP.objects.filter(event__id=event.id)
                    .filter(status="CO")
                    .filter(payment__price__isnull=False)
                    .values_list("payment__price", flat=True)
                )
                average = amount / event.participants_confirmes

                amount_since = sum(
                    RSVP.objects.filter(event__id=event.id)
                    .filter(status="CO")
                    .filter(payment__price__isnull=False)
                    .values_list("payment__price", flat=True)
                )

                participants_since = (
                    RSVP.objects.filter(event__id=event.id)
                    .filter(status="CO")
                    .count()
                )

                average_since = amount_since / participants_since

                message += (
                    f"Pour l'événement <b>{event.name} il y a {event.participants} participants, "
                    f"dont {event.participants_confirmes} confirmés</b>\n"
                    "Le montant total des paiements est de <b>{:.2f}€</b>\n"
                    "Le montant moyen par participant est de <b>{:.2f}€</b>\n\n"
                )

            message += "Bonne journée\n"
            self.stdout.write(message)
        else:
            raise CommandError("You must specify at least one event id")
