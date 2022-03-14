import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from agir.events.actions.notifications import upcoming_event_start_reminder_notification
from agir.events.models import Event

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send upcoming event participants a reminder of the event start"

    def handle(self, **kwargs):
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        one_hour_from_now = timezone.now().replace(
            minute=0, second=0, microsecond=0
        ) + timedelta(hours=1)
        two_hours_from_now = timezone.now().replace(
            minute=0, second=0, microsecond=0
        ) + timedelta(hours=2)

        upcoming_event_pks = (
            Event.objects.listed()
            .upcoming()
            .filter(
                start_time__gte=one_hour_from_now, start_time__lt=two_hours_from_now
            )
            .values_list("pk", flat=True)
        )

        if len(upcoming_event_pks) > 0:
            logger.info(
                f"{now} -- Sending upcoming start reminder for {len(upcoming_event_pks)} event(s) "
                f"({one_hour_from_now} - {two_hours_from_now}). "
            )
            for event_pk in upcoming_event_pks:
                upcoming_event_start_reminder_notification(event_pk)
        else:
            logger.info(
                f"{now} -- No upcoming event start found ({one_hour_from_now} - {two_hours_from_now})."
            )

        logger.info("Done!")
