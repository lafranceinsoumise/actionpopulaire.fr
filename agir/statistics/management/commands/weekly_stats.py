import numpy as np
from django.utils.formats import date_format

from agir.lib.admin.utils import admin_url
from agir.lib.commands import BaseCommand
from ...actions import *
from ...models import AbsoluteStatistics


class Command(BaseCommand):
    help = "Display weekly statistics"
    section_count = 0
    section_item_count = 0
    language = "fr"
    bullets = [" · ", "✶", "✷", "✸", "✹", "✺"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date = AbsoluteStatistics.objects.latest().date
        self.instant = AbsoluteStatistics.objects.values(
            *AbsoluteStatistics.AGGREGATABLE_FIELDS
        ).latest()
        self.last_week = AbsoluteStatistics.objects.aggregate_for_last_week()
        week_start, _ = self.last_week["period"]
        self.last_week_progress = (
            AbsoluteStatistics.objects.aggregate_for_last_week_progress()
        )
        self.current_month = AbsoluteStatistics.objects.aggregate_for_current_month(
            date=week_start
        )
        self.weeks_since_month_start = round(
            (
                np.datetime64(self.current_month["period"][1])
                - np.datetime64(self.current_month["period"][0])
            )
            / np.timedelta64(1, "W")
        )
        self.current_year = AbsoluteStatistics.objects.aggregate_for_current_year(
            date=week_start
        )
        self.weeks_since_year_start = round(
            (
                np.datetime64(self.current_year["period"][1])
                - np.datetime64(self.current_year["period"][0])
            )
            / np.timedelta64(1, "W")
        )

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

    def print_value_line(self, label, value, relative=False):
        if self.section_item_count < len(self.bullets):
            bullet = self.bullets[self.section_item_count]
        else:
            bullet = self.bullets[-1]

        if isinstance(value, str):
            self.log(f" {bullet} {label} : <b>{value}</b>")
        elif relative:
            self.log(f" {bullet} {label} : <b>{value : >+n}</b>")
        else:
            self.log(f" {bullet} {label} : <b>{value : >n}</b>")
        self.section_item_count += 1

    def print_stock(self, key):
        label = AbsoluteStatistics._meta.get_field(key).verbose_name
        self.start_section(label, self.instant[key])
        self.print_value_line(f"cette semaine", self.last_week[key], relative=True)
        self.print_value_line(
            f"par rapport à la semaine précédente",
            self.last_week_progress[key],
            relative=True,
        )
        self.print_value_line(
            f"depuis début {self.date.strftime('%b')}",
            self.current_month[key],
            relative=True,
        )
        self.print_value_line(
            f"en {self.date.year}", self.current_year[key], relative=True
        )
        self.end_section()

    def print_flux(self, key):
        label = AbsoluteStatistics._meta.get_field(key).verbose_name
        average_per_week_since_month_start = (
            self.current_month[key] / self.weeks_since_month_start
        )
        average_per_week_since_year_start = (
            self.current_year[key] / self.weeks_since_year_start
        )

        self.start_section(label)
        self.print_value_line(
            "cette semaine",
            self.last_week[key],
        )
        self.print_value_line(
            "par rapport à la semaine précédente",
            self.last_week_progress[key],
            relative=True,
        )
        self.print_value_line(
            f"depuis début {self.date.strftime('%b')}",
            self.current_month[key],
        )
        self.print_value_line(
            f"en {self.date.year}",
            self.current_year[key],
        )
        self.print_value_line(
            "depuis toujours",
            self.instant[key],
        )
        self.print_value_line(
            "moyenne par semaine depuis le début du mois",
            average_per_week_since_month_start,
        )
        self.print_value_line(
            "moyenne par semaine depuis le début de l'année",
            average_per_week_since_year_start,
        )
        self.end_section()

    def print_largest_campaigns(self):
        start, end = self.last_week["period"]

        largest_campaigns = get_largest_campaign_statistics(start, end)

        if not largest_campaigns:
            self.log("<i>— Aucun gros envoi n'a été fait la semaine dernière.</i>")
            return

        for campaign in largest_campaigns:
            url = admin_url(
                "admin:nuntius_campaign_change", args=(campaign["id"],), absolute=True
            )
            self.start_section(f'« <a href="{url}">{campaign["name"]}</a> »')
            self.print_value_line("Envoyés", campaign["sent_email_count"])
            self.print_value_line("Ouverts", campaign["open_email_count"])

            open_ratio = 0
            if campaign["sent_email_count"] != 0 and campaign["open_email_count"] != 0:
                open_ratio = campaign["open_email_count"] / campaign["sent_email_count"]
            self.print_value_line("Taux d'ouverture", f"{open_ratio : >.2%}")
            self.end_section()

    def handle(self, *args, **options):
        week_start, week_end = self.last_week["period"]
        self.log(
            f"<b>ACTION POPULAIRE · Statistiques hébdomadaires</b>", self.style.WARNING
        )
        self.log(
            f"<i>— du {date_format(week_start)} au {date_format(week_end)} —</i>",
            self.style.SQL_KEYWORD,
        )

        self.print_section_title("Événements")
        self.print_flux("event_count")

        self.print_section_title("Groupes d'action")
        self.print_stock("local_supportgroup_count")
        self.print_stock("local_certified_supportgroup_count")
        self.print_stock("membership_person_count")
        self.print_stock("boucle_departementale_membership_person_count")

        self.print_section_title("Membres LFI")
        self.print_stock("political_support_person_count")

        self.print_section_title("E-mails")
        self.print_stock("lfi_newsletter_subscriber_count")
        self.print_flux("sent_campaign_count")
        self.print_flux("sent_campaign_email_count")

        self.print_section_title("Gros envois d'emails ( >10000 personnes )")
        self.print_largest_campaigns()
