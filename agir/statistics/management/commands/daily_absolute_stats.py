import datetime
import uuid

from django.contrib.humanize.templatetags.humanize import apnumber
from django.db import IntegrityError
from django.utils.translation import ngettext

from agir.event_requests.models import EventSpeakerRequest, EventRequest
from agir.event_requests.tasks import send_new_event_speaker_request_notification
from agir.lib.commands import BaseCommand
from agir.statistics.models import AbsoluteStatistics


class Command(BaseCommand):
    """
    Create or update an AbsoluteStatistics item for the current date's previous day
    """

    help = (
        "Create or update an AbsoluteStatistics item for one particular date. "
        "Defaults to the current date's previous day"
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "-d",
            "--date",
            type=lambda dt: datetime.datetime.strptime(dt, "%Y-%m-%d").date(),
            help="The selected date (formatted as '%Y-%m-%d')",
        )
        parser.add_argument(
            "-f",
            "--force",
            dest="force",
            action="store_true",
            default=False,
            help="Update the existing instance if one exists",
        )

    def create(self, date=None):
        try:
            absolute_stats = AbsoluteStatistics.objects.create(date=date)
        except IntegrityError:
            self.error(
                "An instance for the current date already exists. "
                "If you would like to update the current instance, re-run the commande with the --force flag."
            )
        else:
            self.success(
                f"An instance for the selected date ({absolute_stats.date}) has been successfully created!"
            )

    def update_or_create(self, date=None):
        absolute_stats, created = AbsoluteStatistics.objects.update_or_create(date=date)
        if created:
            self.success(c
                f"An instance for the selected date ({absolute_stats.date}) has been successfully created!"
            )
        else:
            self.success(
                f"The instance for the selected date ({absolute_stats.date}) has been successfully updated!"
            )

    def handle(
        self,
        *args,
        date=None,
        force=False,
        dry_run=False,
        **kwargs,
    ):
        if dry_run:
            self.info(f"Dry-run mode is currently not supported.")
            return

        if date:
            self.info(f"Generating absolute statistics for the selected date: {date}.")
        else:
            self.info(f"Generating absolute statistics for the yesterday's date.")

        if force is True:
            self.update_or_create(date)
        else:
            self.create(date)
