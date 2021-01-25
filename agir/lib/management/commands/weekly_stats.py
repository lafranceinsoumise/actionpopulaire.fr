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

        instant_stats = get_instant_stats()
        main_week_stats = get_general_stats(start, end)
        previous_week_stats = get_general_stats(last_week_start, start)
        twelveweeksstats = get_general_stats(twelveweeksago, end)

        def print_stock(label, key):
            print(
                f"{label} : {instant_stats[key]} ({main_week_stats[key]} / {previous_week_stats[key]} / {twelveweeksstats[key]/12 : > .2f})"
            )

        def print_flux(label, key):
            print(
                f"{label} : {main_week_stats[key]} / {previous_week_stats[key]} / {twelveweeksstats[key]/12 : > .2f}"
            )

        print(
            f"Plateforme - du {date_format(start)} au {date_format(end-timezone.timedelta(days=1))}"
        )

        print(
            "Progression entre parenthèse : cette semaine / semaine précédente / moyenne 3 mois"
        )

        print("\nI) Signataires")
        print_stock("Signataires NSP", "soutiens_NSP")
        print_stock("dont insoumis", "soutiens_NSP_insoumis")
        print_stock("dont non insoumis", "soutiens_NSP_non_insoumis")

        print("\nII) Newsletters")
        print_flux("Ouvertures LFI", "news_LFI")
        print_flux("Ouvertures NSP", "news_NSP")

        print("\nIII) Action populaire")
        print_flux("Connexions", "ap_users")
        print_flux("Dont insoumis", "ap_users_LFI")
        print_flux("Dont NSP (non LFI)", "ap_users_NSP")
        print_flux("Événements", "ap_events")
        print_flux("de la FI", "ap_events_LFI")
        print_flux("de la campagne", "ap_events_NSP")

        print("\nIV) Groupes")
        print_stock("Groupes d'actions LFI", "ga_LFI")
        print(f"dont certifiés : {instant_stats['ga_LFI_certifies']}")
        print_stock("Équipes NSP", "equipes_NSP")
        print_stock("Membres de GA LFI", "membres_ga_LFI")
        print(f"dont de GA certifiés : {instant_stats['membres_ga_LFI_certifies']}")
        print_stock("Membres équipes de soutien NSP", "membres_equipes_NSP")
        print_stock("dont insoumis", "membres_equipes_NSP_insoumis")
        print_stock("dont non insoumis", "membres_equipes_NSP_non_insoumis")

        print("\nV) Progression possible")
        print(f"Insoumis non NSP : {instant_stats['insoumis_non_NSP']}")
        print(
            f"dont mails ouvert 3 derniers mois : {instant_stats['insoumis_non_NSP_newsletter']}"
        )
        print(
            f"dont contactables par SMS : environ {instant_stats['insoumis_non_NSP_phone']}"
        )
