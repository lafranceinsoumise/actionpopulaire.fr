import numpy as np
from django.utils.formats import date_format

from agir.lib.commands import BaseCommand
from agir.statistics.actions import *


class Command(BaseCommand):
    help = "Display weekly statistics - Materiel statistics"
    section_count = 0
    section_item_count = 0
    language = "fr"
    bullets = [" · ", "✶", "✷", "✸", "✹", "✺"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date = MaterielStatistics.objects.latest().date
        week_start = self.date - datetime.timedelta(days=self.date.weekday())
        week_end = week_start + datetime.timedelta(days=6)
        self.week = week_start, week_end

        self.stats = {
            "model": MaterielStatistics,
            "instant": MaterielStatistics.objects.values(
                *MaterielStatistics.AGGREGATABLE_FIELDS
            ).latest(),
            "last_week": MaterielStatistics.objects.aggregate_for_last_week(),
            "last_week_progress": (
                MaterielStatistics.objects.aggregate_for_last_week_progress()
            ),
            "current_month": MaterielStatistics.objects.aggregate_for_current_month(
                date=week_start
            ),
            "current_year": MaterielStatistics.objects.aggregate_for_current_year(
                date=week_start
            ),
        }

    def start_section(self, label, value=None):
        self.section_item_count = 0
        line = f"{label}"
        if isinstance(value, int):
            line += f"  : {value : >n}"
        line = f"<b>{line}</b>"
        self.log(line, self.style.MIGRATE_HEADING)

    def end_section(self):
        self.log("\n")

    def print_section_title(self, title):
        self.section_count += 1
        self.log("\n")
        self.log(f"<b>{self.section_count}) {title.upper()}</b>", self.style.WARNING)
        self.log("\n")

    def print_value_line(self, label, value, relative=False, currency=False):
        if self.section_item_count < len(self.bullets):
            bullet = self.bullets[self.section_item_count]
        else:
            bullet = self.bullets[-1]

        self.section_item_count += 1

        if isinstance(value, str):
            self.log(f" {bullet} {label} : <b>{value}</b>")
            return

        unit = ""
        if currency:
            value = round(value / 100)
            unit = " €"

        if relative:
            self.log(f" {bullet} {label} : <b>{value : >+n}{unit}</b>")
            return

        self.log(f" {bullet} {label} : <b>{value : >n}{unit}</b>")

    def print_stock(self, key, currency=False):
        label = self.stats["model"]._meta.get_field(key).verbose_name

        self.start_section(label, self.stats["instant"][key])
        self.print_value_line(
            f"cette semaine",
            self.stats["last_week"][key],
            relative=True,
            currency=currency,
        )
        self.print_value_line(
            f"par rapport à la semaine précédente",
            self.stats["last_week_progress"][key],
            relative=True,
            currency=currency,
        )
        current_month = self.stats["current_month"]["period"][0].strftime("%b")
        self.print_value_line(
            f"depuis début {current_month}",
            self.stats["current_month"][key],
            relative=True,
            currency=currency,
        )
        current_year = self.stats["current_year"]["period"][0].year
        self.print_value_line(
            f"en {current_year}",
            self.stats["current_year"][key],
            relative=True,
            currency=currency,
        )
        self.end_section()

    def print_flux(self, key, currency=False):
        label = self.stats["model"]._meta.get_field(key).verbose_name

        weeks_since_month_start = round(
            (
                np.datetime64(self.stats["current_month"]["period"][1])
                - np.datetime64(self.stats["current_month"]["period"][0])
            )
            / np.timedelta64(1, "W")
        )

        weeks_since_year_start = round(
            (
                np.datetime64(self.stats["current_year"]["period"][1])
                - np.datetime64(self.stats["current_year"]["period"][0])
            )
            / np.timedelta64(1, "W")
        )

        average_per_week_since_month_start = (
            self.stats["current_month"][key] / weeks_since_month_start
        )
        average_per_week_since_year_start = (
            self.stats["current_year"][key] / weeks_since_year_start
        )

        self.start_section(label)
        self.print_value_line(
            "cette semaine", self.stats["last_week"][key], currency=currency
        )
        self.print_value_line(
            "par rapport à la semaine précédente",
            self.stats["last_week_progress"][key],
            relative=True,
            currency=currency,
        )
        current_month = self.stats["current_month"]["period"][0].strftime("%b")
        self.print_value_line(
            f"depuis début {current_month}",
            self.stats["current_month"][key],
            currency=currency,
        )
        current_year = self.stats["current_year"]["period"][0].year
        self.print_value_line(
            f"en {current_year}", self.stats["current_year"][key], currency=currency
        )
        self.print_value_line(
            "moyenne par semaine depuis le début du mois",
            average_per_week_since_month_start,
            currency=currency,
        )
        self.print_value_line(
            "moyenne par semaine depuis le début de l'année",
            average_per_week_since_year_start,
            currency=currency,
        )
        self.end_section()

    def handle(self, *args, **options):
        week_start, week_end = self.week
        self.log(
            f"<b>ACTION POPULAIRE · Statistiques hébdomadaires</b>", self.style.WARNING
        )
        self.log(
            f"<i>— du {date_format(week_start)} au {date_format(week_end)} —</i>",
            self.style.SQL_KEYWORD,
        )
        self.print_section_title("Site matériel")
        self.print_flux("total_orders")
        self.print_flux("total_items")
        self.print_flux("total_sales", currency=True)
        self.print_flux("total_discount", currency=True)
