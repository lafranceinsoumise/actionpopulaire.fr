import datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.formats import date_format

from agir.lib.management_utils import date_as_local_datetime_argument
from ...stats import *


class Command(BaseCommand):
    help = "Display weekly statistics"

    def add_arguments(self, parser):
        parser.add_argument(
            "start",
            nargs="?",
            default=None,
            metavar="START",
            help="the start date",
            type=date_as_local_datetime_argument,
        )
        parser.add_argument(
            "end",
            nargs="?",
            default=None,
            metavar="END",
            help="then end date (not included)",
            type=date_as_local_datetime_argument,
        )

    def handle(self, *args, start, end, **options):
        period = week = timezone.timedelta(days=7)
        period_name = "semaine"

        today = (
            timezone.now()
            .astimezone(timezone.get_current_timezone())
            .replace(hour=0, minute=0, second=0, microsecond=0)
        )
        last_monday = today - datetime.timedelta(days=today.weekday())

        if start is None:
            end = last_monday
            start = last_monday - period
        else:
            if end is None:
                end = start + week

                if end > today:
                    end = today
                    period = end - start
                    period_name = "période"
            else:
                period = end - start
                if period != week:
                    period_name = "période"

        one_period_before = start - period
        two_period_before = start - 2 * period

        self.stdout.write(
            f"Plateforme - du {date_format(start)} au {date_format(end-timezone.timedelta(days=1))}"
        )
        if period != week:
            self.stdout.write(
                "Attention : durée différente d'une, périodes non directement comparables"
            )
        self.stdout.write("\n")

        main_week_stats = get_general_stats(start, end)
        previous_week_stats = get_general_stats(one_period_before, start)
        earliest_week_stats = get_general_stats(two_period_before, one_period_before)

        print(
            "{} nouveaux signataires ({} la {period} précédente, {} celle d'avant)".format(
                main_week_stats["new_supporters"],
                previous_week_stats["new_supporters"],
                earliest_week_stats["new_supporters"],
                period=period_name,
            )
        )

        print(
            "{} nouveaux groupes ({:+d})".format(
                main_week_stats["new_groups"],
                main_week_stats["new_groups"] - previous_week_stats["new_groups"],
            )
        )

        print(
            "{} évènements survenus ({:+d})".format(
                main_week_stats["events_happened"],
                main_week_stats["events_happened"]
                - previous_week_stats["events_happened"],
            )
        )

        meetings = Event.objects.filter(
            subtype__id__in=[10, 26, 21],
            visibility=Event.VISIBILITY_PUBLIC,
            end_time__range=(start, end),
        ).count()
        last_week_meetings = Event.objects.filter(
            subtype__id__in=[10, 26, 21],
            visibility=Event.VISIBILITY_PUBLIC,
            end_time__range=(one_period_before, start),
        ).count()

        print(
            "dont {} réunions publiques ({:+d})".format(
                meetings, meetings - last_week_meetings
            )
        )

        print(
            "{} personnes ont rejoint leur premier groupe local ({:+d})".format(
                main_week_stats["new_memberships"],
                main_week_stats["new_memberships"]
                - previous_week_stats["new_memberships"],
            )
        )

        print("\nActuellement :\n")

        instant_stats = get_instant_stats()
        print("{} inscrit⋅e⋅s aux emails".format(instant_stats["subscribers"]))
        print("{} membres de groupes".format(instant_stats["group_members"]))
        print(
            "{} membres de groupes certfifiés".format(
                instant_stats["certified_group_members"]
            )
        )
        print("{} groupes locaux".format(instant_stats["groups"]))
        print("{} groupes locaux certifiés".format(instant_stats["certified_groups"]))
        print("{} groupes thématiques".format(instant_stats["thematic_groups"]))
        print("{} groupes fonctionnels".format(instant_stats["func_groups"]))
        print("{} groupes professionnels".format(instant_stats["pro_groups"]))
