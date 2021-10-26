from argparse import FileType
from decimal import Decimal
from io import BytesIO

from django.core.mail import get_connection, EmailMessage
from django.core.management import BaseCommand
from django.db.models import Q
from django.utils import timezone
from glom import glom, Coalesce, T
from xlsxwriter import Workbook

from agir.lib.management_utils import datetime_argument, email_argument
from agir.payments.models import Payment

PAYMENT_SPEC = {
    "créé": "created",
    "dernier événement": "modified",
    "id": "id",
    "email": "email",
    "nom": "last_name",
    "prenom": "first_name",
    "telephone": Coalesce("phone_number.as_international", default=None),
    "statut": T.get_status_display(),
    "montant": ("price", lambda m: Decimal(m) / 100),
    "type": "type",
    "mode": "mode",
    "abonnement associé": "subscription_id",
    "adresse1": Coalesce(T.meta["location_address1"], default=None),
    "adresse2": Coalesce(T.meta["location_address1"], default=None),
    "code postal": Coalesce(T.meta["location_zip"], default=None),
    "ville": Coalesce(T.meta["location_city"], default=None),
    "pays": Coalesce(T.meta["location_country"], default=None),
}


MESSAGE_BODY = """
Bonjour,

Vous trouverez ci-joint l'export des paiements demandé.

Amitiés insoumises,
Action Populaire elle-même
"""


class Command(BaseCommand):
    help = "Exporte les informations supplémentaires nécessaires pour l'audit des paiements"

    def add_arguments(self, parser):
        parser.add_argument(
            "-b",
            "--before",
            type=datetime_argument,
            help="Limite l'extraction aux événements créés avant cette date",
        )
        parser.add_argument(
            "-a",
            "--after",
            type=datetime_argument,
            help="Limite l'extraction aux événements créés après cette date",
        )

        parser.add_argument(
            "-t",
            "--type",
            dest="types",
            action="append",
            metavar="TYPE",
            help="Limiter l'extraction à ce type de paiement. Répéter cette option permet d'inclure plusieurs types.",
        )

        parser.add_argument(
            "-m",
            "--mode",
            dest="modes",
            action="append",
            metavar="MODE",
            help="Limiter l'extraction à ce mode de paiement. Répéter cette option permet d'inclure plusieurs modes.",
        )

        parser.add_argument(
            "--minimum",
            type=int,
            help="Limiter aux paiements d'un montant supérieur ou égal à ce montant.",
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

    def handle(self, before, after, minimum, modes, types, emails, output, **kwargs):
        condition = Q()

        if before:
            condition &= Q(created__lte=before)
        if after:
            condition &= Q(created__gte=after)

        if modes:
            condition &= Q(mode__in=modes)
        if types:
            condition &= Q(type__in=types)

        if minimum:
            condition &= Q(price__gte=minimum)

        payments = glom(
            Payment.objects.filter(condition).order_by("created"), [PAYMENT_SPEC]
        )

        xlsx_content = BytesIO()
        wb = Workbook(xlsx_content, options={"remove_timezone": True})

        default_style = {"border": 1}

        entetes = wb.add_format({"bold": True, "align": "center", **default_style})
        bordures = wb.add_format(default_style)
        montant = wb.add_format(
            {"num_format": "# ##0.00 [$€-40C];-# ##0.00 [$€-40C]", **default_style}
        )
        date = wb.add_format({"num_format": "dd/mm/yyyy", **default_style})

        formats = {
            "montant": montant,
            "créé": date,
            "dernier événement": date,
        }

        ws = wb.add_worksheet("Paiements")
        ws.repeat_rows(0)
        ws.set_column(0, len(PAYMENT_SPEC) - 1, width=16)

        for c, colonne in enumerate(PAYMENT_SPEC.keys()):
            ws.write(0, c, colonne, entetes)

        for l, payment in zip(range(1, len(payments) + 1), payments):
            for c, colonne in enumerate(PAYMENT_SPEC.keys()):
                ws.write(l, c, payment[colonne], formats.get(colonne, bordures))

        wb.close()

        if output:
            output.write(xlsx_content.getvalue())

        if emails:
            connection = get_connection()
            now = timezone.now().strftime("%Y-%m-%d-%H-%M")
            for e in emails:
                message = EmailMessage(
                    subject=f"Export des paiements",
                    body=MESSAGE_BODY,
                    from_email="nepasrepondre@lafranceinsoumise.fr",
                    to=[e],
                    connection=connection,
                )
                message.attach(
                    f"{now}-export-paiements.xlsx",
                    xlsx_content.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
                message.send()
