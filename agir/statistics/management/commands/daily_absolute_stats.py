import datetime

from django.db import IntegrityError

from agir.lib.commands import BaseCommand
from agir.statistics.models import (
    AbsoluteStatistics,
    MaterielStatistics,
    CommuneStatistics,
)
from agir.statistics.utils import get_default_date


class Command(BaseCommand):
    """
    Create or update an AbsoluteStatistics item for the current date's previous day
    """

    help = (
        "Create or update AbsoluteStatistics and MaterielStatistics instances for one particular date. "
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

    def create(self, date):
        try:
            AbsoluteStatistics.objects.create(date=date)
        except IntegrityError:
            self.error(
                "An AbsoluteStatistics instance for the current date already exists. "
                "If you would like to update the current instance, re-run the commande with the --force flag."
            )
        else:
            self.success(
                f"An AbsoluteStatistics instance for the selected date ({date}) has been successfully created!"
            )

        try:
            CommuneStatistics.objects.create_all_for_date(date=date)
        except IntegrityError:
            self.error(
                "Some CommuneStatistics instances for the current date already exist. "
                "If you would like to update the current instances, re-run the commande with the --force flag."
            )
        else:
            self.success(
                f"CommuneStatistics instances for the selected date ({date}) have been successfully created!"
            )

        try:
            MaterielStatistics.objects.create(date=date)
        except IntegrityError:
            self.error(
                "A MaterielStatistics instance for the current date already exists. "
                "If you would like to update the current instance, re-run the commande with the --force flag."
            )
        else:
            self.success(
                f"A MaterielStatistics instance for the selected date ({date}) has been successfully created!"
            )

    def update_or_create(self, date):
        _, created = AbsoluteStatistics.objects.update_or_create(date=date)
        if created:
            self.success(
                f"An AbsoluteStatistics instance for the selected date ({date}) has been successfully created!"
            )
        else:
            self.success(
                f"The AbsoluteStatistics instance for the selected date ({date}) has been successfully updated!"
            )

        CommuneStatistics.objects.update_or_create_all_for_date(date=date)
        self.success(
            f"The CommuneStatistics instance for the selected date ({date}) has been successfully created / updated!"
        )

        _, created = MaterielStatistics.objects.update_or_create(date=date)
        if created:
            self.success(
                f"A MaterielStatistics instance for the selected date ({date}) has been successfully created!"
            )
        else:
            self.success(
                f"The MaterielStatistics instance for the selected date ({date}) has been successfully updated!"
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
            self.info(f"Generating statistics for the selected date: {date}.")
        else:
            date = get_default_date()
            self.info(f"Generating statistics for yesterday's date.")

        if force is True:
            self.update_or_create(date)
        else:
            self.create(date)
