from django.utils.formats import date_format

from agir.lib.commands import BaseCommand
from agir.statistics.models import CommuneStatistics
from agir.statistics.utils import get_commune_count_by_population_range


class Command(BaseCommand):
    help = "Display weekly statistics - Commune statistics"
    section_count = 0
    section_item_count = 0
    language = "fr"
    bullets = [" · ", "✶", "✷", "✸", "✹", "✺"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.date = CommuneStatistics.objects.latest().date
        self.commune_statistics = CommuneStatistics.objects.aggregate_for_date(
            date=self.date
        )
        self.commune_count = get_commune_count_by_population_range()

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
            self.log(f" {bullet} {label} : {value}")
            return

        unit = ""
        if currency:
            value = round(value / 100)
            unit = " €"

        if relative:
            self.log(f" {bullet} {label} : {value : >+n}{unit}")
            return

        self.log(f" {bullet} {label} : {value : >n}{unit}")

    def print_commune_statistics(self, key, title=None):
        data = self.commune_statistics[key]
        label = key
        if CommuneStatistics._meta.get_field(key):
            label = CommuneStatistics._meta.get_field(key).verbose_name

        title = title or f"Communes avec un ou plus {label.lower()}"

        total = data["total"]
        self.start_section(
            f"{title} : {total : >n} ({total / self.commune_count['total']:.2%})"
            if total > 0 and self.commune_count.get("total") > 0
            else f"<b>{total : >n}</b>"
        )

        if total == 0:
            return

        for subkey, subvalue in data.items():
            if subkey == "total":
                continue
            sublabel = (
                f"{subkey[0]: >n} à {subkey[1] + 1: >n} hab."
                if len(subkey) == 2
                else f"{subkey[0]: >n} hab. et plus"
            )
            subvalue = (
                f"<b>{subvalue / self.commune_count[subkey]:.2%}</b> "
                f"(<em><b>{subvalue : >n}</b>／{self.commune_count[subkey] : >n}</em>)"
                if subvalue > 0 and self.commune_count.get(subkey, 0) > 0
                else f"<b>{subvalue : >n}</b>"
            )
            self.print_value_line(sublabel, subvalue)

        self.end_section()

    def handle(self, *args, **options):
        self.log(
            f"<b>ACTION POPULAIRE · Statistiques par communes</b>", self.style.WARNING
        )
        self.log(
            f"<i>— le {date_format(self.date)} —</i>",
            self.style.SQL_KEYWORD,
        )

        self.print_section_title("Groupes d'action")
        self.print_commune_statistics("local_supportgroup_count")
        self.print_commune_statistics("local_certified_supportgroup_count")
        self.print_section_title("Événements")
        self.print_commune_statistics("event_count")
        self.print_section_title("Personnes")
        self.print_commune_statistics(
            "people_count", title="Communes avec au moins une personne"
        )
