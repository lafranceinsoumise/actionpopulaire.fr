from argparse import FileType
from io import BytesIO

import pandas as pd
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.core.management.base import BaseCommand
from django.utils import timezone
from glom import Coalesce, T, glom

from agir.lib.management_utils import month_argument, month_range, email_argument
from agir.payments.models import Payment
from agir.system_pay.models import SystemPayTransaction

FILE_DESC = {
    "Code_uuid": (
        "systempaytransaction_set",
        T.get(status=SystemPayTransaction.STATUS_COMPLETED),
        "uuid",
        T.hex,
    ),
    "No_abonnement": "subscription.id",
    "Email": Coalesce("person.email", "email"),
    "Nom": Coalesce("person.last_name", "subscription.meta.last_name"),
    "Prénom": Coalesce(
        "person.first_name", "subscription.meta.first_name", skip=("",), default=""
    ),
    "No_et_Voie": Coalesce(
        "person.location_address1",
        "subscription.meta.location_address1",
        skip=("",),
        default="",
    ),
    "Lieu_dit": Coalesce(
        "person.location_address2",
        "subscription.meta.location_address2",
        skip=("",),
        default="",
    ),
    "Code_Postal": Coalesce(
        "person.location_zip", "subscription.meta.location_zip", skip=("",), default=""
    ),
    "Ville": Coalesce(
        "person.location_city",
        "subscription.meta.location_city",
        skip=("",),
        default="",
    ),
    "Pays": (
        Coalesce(
            "person.location_country",
            "subscription.meta.location_country",
            skip=("",),
            default="",
        ),
        str,
    ),
    "Nationalité": "subscription.meta.nationality",
    "Téléphone": Coalesce(
        ("person.contact_phone", T.as_e164), "subscription.meta.contact_phone"
    ),
}


MESSAGE_BODY = """
Bonjour,

Vous trouverez ci-joint l'export des abonnements pour le mois concerné.

Amitiés insoumises,
La gentille plateforme de la France insoumise
"""


class Command(BaseCommand):
    help = "Exporte les informations supplémentaires nécessaires pour l'audit des dons réguliers"

    def add_arguments(self, parser):
        parser.add_argument(
            "month",
            type=month_argument,
            metavar="MONTH",
            help="Le mois pour lequel extraire les abonnements",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="types",
            action="append",
            metavar="TYPE",
            help="Type de souscription à exporter (utiliser plusieurs fois si plusieurs types)",
        )
        parser.add_argument(
            "-s",
            "--send-to",
            dest="emails",
            action="append",
            type=email_argument,
            metavar="EMAIL",
            help="Un email auquel envoyer l'extraction (utilisation multiple possible)",
        )
        parser.add_argument(
            "-o",
            "--output-to",
            dest="output",
            type=FileType(mode="wb"),
            help="Le chemin où sauvegarder l'extraction.",
        )

    def handle(self, *args, month, types, emails, output, **options):
        if month is None:
            now = timezone.now()
            month = month_range(now.year, now.month)

        payments = (
            Payment.objects.filter(
                status=Payment.STATUS_COMPLETED,
                created__range=month,
            )
            .select_related("subscription", "person")
            .prefetch_related("systempaytransaction_set")
        )

        if types:
            payments = payments.filter(subscription__type__in=types)
        else:
            payments = payments.filter(subscription__isnull=False)

        results = glom(payments, [FILE_DESC])

        df = pd.DataFrame(results)
        xlsx_buffer = BytesIO()
        df.to_excel(xlsx_buffer, engine="xlsxwriter", index=False)
        xlsx_file = xlsx_buffer.getvalue()

        if not output and not emails:
            self.stdout.buffer.write(xlsx_file)

        if output:
            output.write(xlsx_file)

        if emails:
            connection = get_connection()

            with connection:
                for e in emails:

                    message = EmailMessage(
                        subject=f"Export des abonnements — {month[0].strftime('%m/%Y')}",
                        body=MESSAGE_BODY,
                        from_email=settings.EMAIL_FROM_LFI,
                        to=[e],
                        connection=connection,
                    )
                    message.attach(
                        f"export-{month[0].strftime('%m-%Y')}.xlsx",
                        xlsx_file,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    message.send()
