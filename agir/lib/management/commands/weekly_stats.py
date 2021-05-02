import datetime

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.formats import date_format
from nuntius.models import Campaign

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
                f"{label} : {instant_stats[key]} __({main_week_stats[key] : >+d} / {previous_week_stats[key] : >+d} / {twelveweeksstats[key]/12 : >+.2f})__"
            )

        def print_flux(label, key):
            print(
                f"{label} : {main_week_stats[key] : >+d} / {previous_week_stats[key] : >+d} / {twelveweeksstats[key]/12 : >+.2f}"
            )

        print(
            f"**Plateforme - du {date_format(start)} au {date_format(end-timezone.timedelta(days=1))}**"
        )

        print(
            "__Progression entre parenthèse : cette semaine / semaine précédente / moyenne 3 mois__"
        )

        print("**\nI) Signataires**")
        print_stock("Signataires NSP", "soutiens_NSP")
        print_stock("dont insoumis", "soutiens_NSP_insoumis")
        print_stock("dont non insoumis", "soutiens_NSP_non_insoumis")

        print("**\nII) Email**")
        print_flux("Total insoumis (signataires NSP) ayant ouvert un email", "news_LFI")
        print(
            f"Taux d'ouverture Insoumis : {main_week_stats['taux_news_LFI'] : > .2f} % / "
            f"{previous_week_stats['taux_news_LFI'] : > .2f} % / {twelveweeksstats['taux_news_LFI'] : > .2f} %"
        )
        print_flux(
            "Total signataires NSP (non-insoumis) ayant ouvert un email", "news_NSP"
        )
        print(
            f"Taux d'ouverture NSP : {main_week_stats['taux_news_NSP'] : > .2f} % / "
            f"{previous_week_stats['taux_news_NSP'] : > .2f} % / {twelveweeksstats['taux_news_NSP'] : > .2f} %"
        )
        print("**Emails de la semaine**")
        for c in Campaign.objects.filter(created__range=(start, end)):
            sent = c.get_sent_count()
            if sent < 5000:
                continue
            open = c.get_unique_open_count()
            click = c.get_unique_click_count()
            print(
                f"{c.name} : {sent} envoyés, {open} ({open/sent * 100 : > .2f} %) "
                f"ouvertures, {click} ({click/sent * 100 : > .2f} %) clics"
            )

        print("**\nIII) Action populaire**")
        print_flux("Connexions", "ap_users")
        print_flux("Dont insoumis", "ap_users_LFI")
        print_flux("Dont NSP (non LFI)", "ap_users_NSP")
        print_flux("Événements", "ap_events")
        print_flux("de la FI", "ap_events_LFI")
        print_flux("de la campagne", "ap_events_NSP")

        print("**\nIV) Groupes**")
        print_stock("Groupes d'actions LFI", "ga_LFI")
        print(f"dont certifiés : {instant_stats['ga_LFI_certifies']}")
        print_stock("Équipes NSP", "equipes_NSP")
        print_stock("Membres de GA LFI", "membres_ga_LFI")
        print(f"dont de GA certifiés : {instant_stats['membres_ga_LFI_certifies']}")
        print_stock("Membres équipes de soutien NSP", "membres_equipes_NSP")
        print_stock("dont insoumis", "membres_equipes_NSP_insoumis")
        print_stock("dont non insoumis", "membres_equipes_NSP_non_insoumis")

        print("**\nV) Progression possible**")
        print(f"Insoumis non NSP : {instant_stats['insoumis_non_NSP']}")
        print(
            f"dont mails ouvert 3 derniers mois : {instant_stats['insoumis_non_NSP_newsletter']}"
        )
        print(
            f"dont contactables par SMS : environ {instant_stats['insoumis_non_NSP_phone']}"
        )
