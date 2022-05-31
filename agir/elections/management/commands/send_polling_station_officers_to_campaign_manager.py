import argparse
import uuid
from time import sleep

from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime
from tqdm import tqdm

from agir.elections.data import campaign_managers_by_circo
from agir.elections.models import PollingStationOfficer
from agir.elections.tasks import send_new_polling_station_officer_to_campaign_manager


def valid_uuid(string):
    try:
        return uuid.UUID(string)
    except ValueError:
        msg = f"not a valid uuid: {string}"
        raise argparse.ArgumentTypeError(msg)


def valid_date(string):
    if not string:
        return string
    try:
        return datetime.strptime(string, "%Y-%m-%d")
    except ValueError:
        msg = f"not a valid date: {string}"
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    """
    Send reminder for non-confirmed accepted voting proxy requests
    """

    help = "Send polling station officer information to campaign managers"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.tqdm = None
        self.dry_run = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--before",
            dest="created_before",
            type=valid_date,
            default="",
            help="YYYY-MM-DD. Send only polling station officers created before this date (not included)",
        )
        parser.add_argument(
            "--id",
            dest="only_ids",
            action="extend",
            nargs="*",
            type=valid_uuid,
            default=[],
            help="Send only officers with these ids",
        )
        parser.add_argument(
            "--email",
            dest="only_emails",
            action="extend",
            nargs="*",
            type=str,
            default=[],
            help="Send only officers with these email addresses",
        )
        parser.add_argument(
            "--circo",
            dest="only_circonscriptions_legislatives",
            action="extend",
            nargs="*",
            type=str,
            default=[],
            help="Send only officers with these circonscription legislative codes",
        )
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            default=False,
            help="Execute without actually sending any notification or updating data",
        )
        parser.add_argument(
            "-s",
            "--silent",
            dest="silent",
            action="store_true",
            default=False,
            help="Display a progress bar during the script execution",
        )

    def log(self, message):
        self.tqdm.write(message)

    def send_reminder(self, polling_station_officer_id):
        if not self.dry_run:
            send_new_polling_station_officer_to_campaign_manager.delay(
                polling_station_officer_id
            )

    def get_queryset(
        self,
        *args,
        created_before=None,
        only_ids=None,
        only_emails=None,
        only_circonscriptions_legislatives=None,
        **kwargs,
    ):
        polling_station_officers = PollingStationOfficer.objects.filter(
            voting_circonscription_legislative__code__in=campaign_managers_by_circo.keys()
        )
        if created_before:
            polling_station_officers = polling_station_officers.filter(
                created__date__lt=created_before
            )
        if only_ids:
            polling_station_officers = polling_station_officers.filter(id__in=only_ids)
        if only_emails:
            polling_station_officers = polling_station_officers.filter(
                contact_email__in=only_emails
            )
        if only_circonscriptions_legislatives:
            polling_station_officers = polling_station_officers.filter(
                voting_circonscription_legislative__code__in=only_circonscriptions_legislatives
            )

        return polling_station_officers.values_list("id", flat=True)

    def handle(
        self,
        *args,
        dry_run=False,
        silent=False,
        **kwargs,
    ):
        self.dry_run = dry_run
        polling_station_officer_ids = self.get_queryset(**kwargs)
        count = len(polling_station_officer_ids)
        self.tqdm = tqdm(
            total=count,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
            disable=silent,
            leave=False,
        )
        if count == 0:
            self.log("\n\nNo polling station officer sent to campaign managers")
            self.log("Bye!\n\n")
            return
        self.log(f"\n\nSending {count} polling station officers to campaign managers")
        for polling_station_officer_id in polling_station_officer_ids:
            self.send_reminder(polling_station_officer_id)
            self.tqdm.update(1)
        self.log("Bye!\n\n")
        self.tqdm.close()
