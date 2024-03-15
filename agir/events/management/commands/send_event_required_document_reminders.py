import logging
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from agir.events.actions.notifications import (
    event_required_document_reminder_notification,
)
from agir.events.actions.required_documents import get_project_missing_document_count
from agir.events.models import Event
from agir.events.tasks import (
    send_pre_event_required_documents_reminder_email,
    send_post_event_required_documents_reminder_email,
)
from agir.gestion.models import Projet
from agir.lib.management_utils import event_argument

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send reminder email/push to organizers of events with missing required documents"

    def add_arguments(self, parser):
        parser.add_argument(
            "-e",
            "--event",
            type=event_argument,
            help="The id of a single event to send the reminder to -- if not specified, reminders will be sent to all events "
            "with missing documents ended yesterday or starting tomorrow",
        )

    def handle(self, event, **kwargs):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        if event is not None:
            try:
                project = Projet.objects.exclude(etat__in=Projet.ETATS_FINAUX).get(
                    event=event
                )
            except Projet.DoesNotExist:
                self.stderr.write(f"No project found for event {event.id}!")
                return

            if get_project_missing_document_count(project) == 0:
                self.stderr.write(
                    f"No missing documents found for event {event.id} (project id: { project.id})"
                )
                return

            if event.end_time < today:
                logger.info(
                    f"Sending post-event missing document reminder to event {event.id}."
                )
                send_post_event_required_documents_reminder_email.delay(event.pk)
                event_required_document_reminder_notification(event.pk, post=True)
            elif event.start_time >= tomorrow:
                logger.info(
                    f"Sending pre-event missing document reminder to event {event.id}."
                )
                send_pre_event_required_documents_reminder_email.delay(event.pk)
                event_required_document_reminder_notification(event.pk, pre=True)
        else:
            yesterday_event_pks = [
                project.event_id
                for project in Projet.objects.filter(
                    event__visibility=Event.VISIBILITY_PUBLIC,
                    event__end_time__date=yesterday.date(),
                )
                if get_project_missing_document_count(project) > 0
            ]
            logger.info(
                f"Sending reminder for {len(yesterday_event_pks)} event(s) ended yesterday ({yesterday.date()})."
            )
            for event_pk in yesterday_event_pks:
                send_post_event_required_documents_reminder_email.delay(event_pk)
                event_required_document_reminder_notification(event_pk, post=True)

            tomorrow_event_pks = [
                project.event_id
                for project in Projet.objects.exclude(
                    etat__in=Projet.ETATS_FINAUX
                ).filter(
                    event__visibility=Event.VISIBILITY_PUBLIC,
                    event__start_time__date=tomorrow.date(),
                )
                if get_project_missing_document_count(project) > 0
            ]
            logger.info(
                f"Sending reminder for {len(tomorrow_event_pks)} event(s) starting tomorrow ({tomorrow.date()})."
            )
            for event_pk in tomorrow_event_pks:
                send_pre_event_required_documents_reminder_email.delay(event_pk)
                event_required_document_reminder_notification(event_pk, pre=True)

        logger.info("Done!")
