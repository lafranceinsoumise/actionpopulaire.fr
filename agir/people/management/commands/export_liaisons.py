import csv
import io
from datetime import timedelta
from email.mime.text import MIMEText

from django.core.management import BaseCommand
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.timezone import make_aware
from slugify import slugify

from agir.lib.mailing import send_message
from agir.people.models import Person

EXPORT_EMAIL_SUBJECT_ALL = "Export de tout·es les correspondant·es d'immeuble"
EXPORT_EMAIL_SUBJECT_PERIOD = (
    "Export des correspondant·es d'immeuble ajouté·es entre le %s et le %s"
)
EXPORT_EMAIL_BODY = """
Bonjour.

Ci-joint l'%s :

%s

Cordialement.

L'équipe d'Action populaire.
"""

CSV_FIELDS = [
    ("email", "email"),
    ("last_name", "nom"),
    ("first_name", "prénom"),
    ("location_address1", "adresse"),
    ("location_address2", "complément"),
    ("location_zip", "code postal"),
    ("location_city", "ville"),
    ("location_country", "pays"),
    ("contact_phone", "téléphone"),
    ("liaison_date", "date"),
    ("id", "id"),
]


class Command(BaseCommand):
    """
    Export people having accepted the 2022 liaison type newsletter, optionnally sending the list
    as a CSV file email attachment.

    Examples:

    $ export_liaisons                                           Print liaison people added during the last 7 days
    $ export_liaisons -a                                        Print all liaison people
    $ export_liaisons --from '01/01/2021'                       Print all liaison people added since a given date
    $ export_liaisons --from '01/01/2021' --to '01/01/2021'     Print all liaison people added between two given dates
    $ export_liaisons -e email@example.com                      Create and email a CSV file for liaison people
                                                                added during the last 7 days
    """

    help = "Export people having accepted the 2022 liaison type newsletter, optionnally sending the list as a CSV file email attachment."

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--all",
            dest="all",
            action="store_true",
            default=False,
            help="Export all liaison people",
        )
        parser.add_argument(
            "--from",
            dest="from_date",
            default=None,
            help="Limit results to liaisons added after this date (DD-MM-YYYY)",
        )
        parser.add_argument(
            "--to",
            dest="to_date",
            default=None,
            help="Limit results to liaisons added before this date (DD-MM-YYYY)",
        )
        parser.add_argument(
            "-e",
            "--email",
            dest="emails",
            default=None,
            help="An optional comma-separated list of email addresses to send the export to",
        )

    def get_liaisons(self, all=False, from_date=None, to_date=None):
        if all:
            return Person.objects.liaisons(), EXPORT_EMAIL_SUBJECT_ALL

        if to_date is not None:
            to_date = make_aware(datetime.strptime(to_date, "%d-%m-%Y"))
        else:
            to_date = timezone.now()

        if from_date is not None:
            from_date = make_aware(datetime.strptime(from_date, "%d-%m-%Y"))
        else:
            from_date = to_date - timedelta(days=7)

        return (
            Person.objects.liaisons(from_date=from_date, to_date=to_date),
            EXPORT_EMAIL_SUBJECT_PERIOD
            % (from_date.strftime("%d/%m/%Y"), to_date.strftime("%d/%m/%Y")),
        )

    def get_csv_string(self, queryset):
        output = io.StringIO()
        writer = csv.writer(output, delimiter=",", lineterminator="\n")
        writer.writerow([label for key, label in CSV_FIELDS])

        for liaison in queryset:
            writer.writerow([getattr(liaison, key) for (key, label) in CSV_FIELDS])

        return output.getvalue()

    def send_email(self, email, subject, csv_string):
        attachment = MIMEText(csv_string)
        attachment.add_header("Content-Type", "text/csv")
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=f"{slugify(subject.lower())}.csv",
        )

        send_message(
            from_email="robot@actionpopulaire.fr",
            subject=subject,
            recipient=email,
            text=EXPORT_EMAIL_BODY % (subject.lower(), csv_string),
            attachments=(attachment,),
        )

    def handle(self, all=False, from_date=None, to_date=None, emails=None, **kwargs):
        (queryset, subject) = self.get_liaisons(
            all=all, from_date=from_date, to_date=to_date
        )

        if not queryset.exists():
            self.stderr.write("― Aucun·e correspondant·e d'immeuble trouvé !")
            return

        self.stdout.write(f"― {subject}\n")

        csv_string = self.get_csv_string(queryset)

        if emails:
            self.send_email(emails.split(","), subject, csv_string)
            self.stdout.write(
                f"― {queryset.count()} correspondant·es d'immeuble trouvé·es."
            )
            self.stdout.write(f"― Un e-mail a été envoyé à : {emails}")
        else:
            self.stdout.write(
                f"― {queryset.count()} correspondant·es d'immeuble trouvé·es :\n\n"
            )
            self.stdout.write(f"{csv_string}\n")

        self.stdout.write("― Au revoir !\n")
