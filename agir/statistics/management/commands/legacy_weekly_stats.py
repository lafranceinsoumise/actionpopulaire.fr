from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.formats import date_format, time_format

from ...legacy_actions import *


class Command(BaseCommand):
    help = "Display weekly statistics"
    section_count = 0

    def print_section_title(self, title):
        self.section_count += 1
        self.stdout.write(f"\n{self.section_count}) ** {title} **", self.style.WARNING)

    def print_line(self, line):
        self.stdout.write(f"   {line}")

    def handle(self, *args, **options):
        today = timezone.now().astimezone(timezone.get_current_timezone())

        if today.isoweekday() != 7 or today.hour < 20:
            last_sunday = today - datetime.timedelta(days=today.isoweekday())
        else:
            last_sunday = today

        last_sunday_8pm = last_sunday.replace(
            hour=20, minute=0, second=0, microsecond=0
        )

        end = last_sunday_8pm
        start = last_sunday_8pm - timezone.timedelta(days=7)
        last_week_start = start - timezone.timedelta(days=7)
        twelveweeksago = start - timezone.timedelta(days=7 * 12)

        instant_stats = get_instant_stats()
        main_week_stats = get_general_stats(start, end)
        previous_week_stats = get_general_stats(last_week_start, start)
        twelveweeksstats = get_general_stats(twelveweeksago, end)

        def print_stock(label, key):
            self.print_line(
                f"{label} : {instant_stats[key]} __({main_week_stats[key] : >+d} / {previous_week_stats[key] : >+d} / {twelveweeksstats[key]/12 : >+.2f})__"
            )

        def print_flux(label, key):
            self.print_line(
                f"{label} : {main_week_stats[key] : >+d} / {previous_week_stats[key] : >+d} / {twelveweeksstats[key]/12 : >+.2f}"
            )

        self.stdout.write("\n")
        self.stdout.write(
            f"** Plateforme — statistiques hébdomadaires **",
            self.style.WARNING,
        )
        self.stdout.write(
            f"du {date_format(start)} {time_format(start)} au {date_format(end)} {time_format(end)}",
            self.style.SQL_KEYWORD,
        )
        self.stdout.write(
            "__Progression entre parenthèse : cette semaine / semaine précédente / moyenne 3 mois__"
        )
        self.stdout.write("\n")

        # SIGNATAIRES
        self.print_section_title("Signataires")
        print_stock("Signataires 2022", "soutiens_2022")
        print_stock(" ├── dont insoumis", "soutiens_2022_insoumis")
        print_stock(" └── dont non insoumis", "soutiens_2022_non_insoumis")

        # EMAILS
        self.print_section_title("Emails")
        print_flux(
            "Total insoumis (signataires 2022) ayant ouvert un email", "news_LFI"
        )
        self.print_line(
            f"Taux d'ouverture Insoumis : {main_week_stats['taux_news_LFI'] : > .2f} % / "
            f"{previous_week_stats['taux_news_LFI'] : > .2f} % / {twelveweeksstats['taux_news_LFI'] : > .2f} %"
        )
        print_flux(
            "Total signataires 2022 (non-insoumis) ayant ouvert un email", "news_2022"
        )
        self.print_line(
            f"Taux d'ouverture 2022 : {main_week_stats['taux_news_2022'] : > .2f} % / "
            f"{previous_week_stats['taux_news_2022'] : > .2f} % / {twelveweeksstats['taux_news_2022'] : > .2f} %"
        )

        # EMAILS DE LA SEMAINE
        self.print_section_title("Emails de la semaine")
        email_count = 0
        for c in Campaign.objects.filter(created__range=(start, end)):
            sent = c.get_sent_count()
            if sent < 5000:
                continue
            open = c.get_unique_open_count()
            click = c.get_unique_click_count()
            self.print_line(
                f"{c.name} : {sent} envoyés, {open} ({open/sent * 100 : > .2f} %) "
                f"ouvertures, {click} ({click/sent * 100 : > .2f} %) clics"
            )
            email_count += 1

        if email_count == 0:
            self.print_line("__Aucun e-mail envoyé cette semaine__")

        self.print_section_title("Événements")
        print_flux("Événements", "ap_events")
        for subtype in EVENT_SUBTYPES.keys():
            print_flux(f"├── dont {subtype.capitalize()}", f"ap_events__{subtype}")

        # GROUPES
        self.print_section_title("Groupes")
        print_stock("Groupes d'actions", "ga")
        self.print_line(f" └── dont certifiés : {instant_stats['ga_certifies']}")
        print_stock("Membres de GA", "membres_ga")
        self.print_line(
            f" └── dont de GA certifiés : {instant_stats['membres_ga_certifies']}"
        )
        print_stock("Membres actifs de GA", "membres_ga_actifs")
        self.print_line(
            f" └── dont de GA certifiés : {instant_stats['membres_ga_certifies_actifs']}"
        )
        print_stock("Contacts de GA", "membres_ga_contacts")
        self.print_line(
            f" └── dont de GA certifiés : {instant_stats['membres_ga_certifies_contacts']}"
        )

        # CONTACTS & CORRESPONDANT·ES D'IMMEUBLE
        self.print_section_title("Contacts & Correspondant·es d'immeuble")
        print_stock("Contacts ajoutés", "contacts")
        print_stock("Correspondant·es d'immeuble", "liaisons")
        print_stock(" ├── dont contacts", "liaisons_contacts")
        print_stock(" └── dont auto-ajoutés", "liaisons_auto")

        # VOTING PROXIES
        self.print_section_title("Procurations")
        print_stock("Invitations envoyées", "voting_proxy_candidates")
        print_stock("Volontaires", "voting_proxies")
        print_stock("Demandes de procurations", "voting_proxy_requests")
        print_stock(" ├── en attente", "voting_proxy_requests__created")
        print_stock(" ├── acceptées", "voting_proxy_requests__accepted")
        print_stock(" └── confirmées", "voting_proxy_requests__confirmed")

        # PROGRESSION POSSIBLE
        self.print_section_title("Progression possible")
        self.print_line(f"Insoumis non 2022 : {instant_stats['insoumis_non_2022']}")
        self.print_line(
            f" ├── dont mails ouvert 3 derniers mois : {instant_stats['insoumis_non_2022_newsletter']}"
        )
        self.print_line(
            f" └── dont contactables par SMS : environ {instant_stats['insoumis_non_2022_phone']}"
        )

        self.stdout.write("\n\n\n")
