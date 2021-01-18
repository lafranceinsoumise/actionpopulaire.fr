import datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.formats import date_format

from ...stats import *


class Command(BaseCommand):
    help = "Display weekly statistics"

    def handle(self, *args, **options):
        today = (
            timezone.now()
            .astimezone(timezone.get_current_timezone())
            .replace(hour=0, minute=0, second=0, microsecond=0)
        )
        last_monday = today - datetime.timedelta(days=today.weekday())

        end = last_monday
        start = last_monday - timezone.timedelta(days=7)
        last_week_start = start - timezone.timedelta(days=7)
        twelveweeksago = start - timezone.timedelta(days=7 * 12)

        print(
            f"Plateforme - du {date_format(start)} au {date_format(end-timezone.timedelta(days=1))}"
        )

        print("Cette semaine / semaine précédente / moyenne 3 mois")

        main_week_stats = get_general_stats(start, end)
        previous_week_stats = get_general_stats(last_week_start, start)
        twelveweeksstats = get_general_stats(twelveweeksago, end)

        for key in main_week_stats.keys():
            print(f"\n{key} :")
            if main_week_stats[key] > twelveweeksstats[key] / 12:
                arrow = "↗️"
            elif main_week_stats[key] > twelveweeksstats[key] / 12:
                arrow = "↘️"
            else:
                arrow = "➡️"
            print(
                f"{arrow} {main_week_stats[key]} / {previous_week_stats[key]} / {twelveweeksstats[key]/12 : > .2f}"
            )

        print("\nActuellement :\n")

        instant_stats = get_instant_stats()

        for key, value in instant_stats.items():
            print(f"{key} : {value}")
