import numpy as np
from django.utils.formats import date_format

from agir.lib.admin.utils import admin_url
from agir.lib.commands import BaseCommand
from ...actions import *
from ...models import AbsoluteStatistics


class Command(BaseCommand):
    help = "Display weekly statistics"
    section_count = 0
    language = "fr"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date = AbsoluteStatistics.objects.latest().date
        self.instant = AbsoluteStatistics.objects.values(
            *AbsoluteStatistics.AGGREGATABLE_FIELDS
        ).latest()
        self.last_week = AbsoluteStatistics.objects.aggregate_for_last_week()
        self.last_week_progress = (
            AbsoluteStatistics.objects.aggregate_for_last_week_progress()
        )
        self.current_month = AbsoluteStatistics.objects.aggregate_for_current_month()
        self.weeks_since_month_start = round(
            (
                np.datetime64(self.current_month["period"][1])
                - np.datetime64(self.current_month["period"][0])
            )
            / np.timedelta64(1, "W")
        )
        self.current_year = AbsoluteStatistics.objects.aggregate_for_current_year()
        self.weeks_since_year_start = round(
            (
                np.datetime64(self.current_year["period"][1])
                - np.datetime64(self.current_year["period"][0])
            )
            / np.timedelta64(1, "W")
        )

    def print_line(self, line, *args, **kwargs):
        self.log(f"   {line}", *args, **kwargs)

    def print_first_line(self, label, value=None):
        line = f"** {label} **"
        if isinstance(value, int):
            line += f" : {value : >n}"
        underline = "‾" * (len(line) + 2)
        self.print_line(line, self.style.MIGRATE_HEADING)
        self.print_line(underline, self.style.MIGRATE_HEADING)

    def print_section_title(self, title):
        self.section_count += 1
        self.log(
            f"\n__ {self.section_count}) {title.upper()} __\n\n", self.style.WARNING
        )

    def print_stock(self, key):
        label = AbsoluteStatistics._meta.get_field(key).verbose_name
        week_start, week_end = self.last_week["period"]
        self.print_first_line(label, self.instant[key])
        self.print_line(
            f" ✶ du {date_format(week_start)} au {date_format(week_end)} : {self.last_week[key] : >+n}"
        )
        self.print_line(
            f" ✷ par rapport à la semaine précédente : {self.last_week_progress[key] : >+n}"
        )
        self.print_line(
            f" ✸ depuis début {self.date.strftime('%b')}: {self.current_month[key] : >+n}"
        )
        self.print_line(f" ✹ en {self.date.year}: {self.current_year[key] : >+n}")
        self.print_line("\n")

    def print_flux(self, key):
        label = AbsoluteStatistics._meta.get_field(key).verbose_name
        week_start, week_end = self.last_week["period"]

        average_per_week_since_month_start = (
            self.current_month[key] / self.weeks_since_month_start
        )
        average_per_week_since_year_start = (
            self.current_year[key] / self.weeks_since_year_start
        )

        self.print_first_line(label, self.instant[key])
        self.print_line(
            f" ✶ du {date_format(week_start)} au {date_format(week_end)} : {self.last_week[key] : >d}"
        )
        self.print_line(
            f" ✷ par rapport à la semaine précédente : {self.last_week_progress[key] : >+n}"
        )
        self.print_line(
            f" ✸ depuis début {self.date.strftime('%b')}: {self.current_month[key] : >d}"
        )
        self.print_line(f" ✹ en {self.date.year}: {self.current_year[key] : >d}")
        self.print_line(
            f" ✺ moyenne par semaine depuis le début du mois : {average_per_week_since_month_start  : >.3n}"
        )
        self.print_line(
            f" ✺ moyenne par semaine depuis le début de l'année : {average_per_week_since_year_start  : >.3n}"
        )
        self.print_line("\n")

    def print_largest_campaigns(self):
        start, end = self.last_week["period"]

        largest_campaigns = get_largest_campaign_statistics(start, end)

        if not largest_campaigns:
            self.print_line("__ Aucun gros envoi n'a été fait la semaine dernière. __")
            return

        for campaign in largest_campaigns:
            self.print_first_line(f"« {campaign['name']} »")
            self.print_line(f" ✶ Envoyés : {campaign['sent_email_count']}")
            self.print_line(f" ✷ Ouverts : {campaign['open_email_count']}")
            if campaign["sent_email_count"] == 0 or campaign["open_email_count"] == 0:
                self.print_line(" ✸ Taux d'ouverture : 0")
            else:
                open_ratio = campaign["open_email_count"] / campaign["sent_email_count"]
                self.print_line(f" ✹ Taux d'ouverture : {open_ratio : >.2%}")
            self.print_line(
                f" ➡ {admin_url('admin:nuntius_campaign_change', args=(campaign['id'],), absolute=True)}"
            )
            self.print_line("\n")

    def handle(self, *args, **options):
        week_start, week_end = self.last_week["period"]
        self.log(
            f"** Action Populaire — statistiques hébdomadaires **", self.style.WARNING
        )
        self.print_line(
            f"du {date_format(week_start)} au {date_format(week_end)}",
            self.style.SQL_KEYWORD,
        )
        self.log("\n")

        self.print_section_title("Événements")
        self.print_flux("event_count")

        self.print_section_title("Groupes d'action")
        self.print_stock("local_supportgroup_count")
        self.print_stock("local_certified_supportgroup_count")

        self.print_section_title("Membres LFI")
        self.print_stock("political_support_person_count")

        self.print_section_title("Membres de groupe d'action locaux")
        self.print_stock("membership_person_count")

        self.print_section_title("Membres des boucles départementales")
        self.print_stock("boucle_departementale_membership_person_count")

        self.print_section_title("E-mails")
        self.print_stock("lfi_newsletter_subscriber_count")
        self.print_flux("sent_campaign_count")
        self.print_flux("sent_campaign_email_count")

        self.print_section_title("Gros envois d'emails (>10000 personnes)")
        self.print_largest_campaigns()
