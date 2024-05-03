import logging
from argparse import FileType, ArgumentTypeError
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.core.mail import get_connection, EmailMessage
from django.db.models import Q
from django.utils import timezone
from glom import glom, Coalesce, T
from xlsxwriter import Workbook

from agir.lib.management_utils import datetime_argument, email_argument, LoggingCommand
from agir.payments.models import Payment
from agir.payments.payment_modes import PAYMENT_MODES
from agir.payments.types import PAYMENT_TYPES

logger = logging.getLogger(__name__)


def date_locale(d):
    return d.astimezone(timezone.get_current_timezone())


PAYMENT_SPEC = {
    "créé": ("created", date_locale),
    "dernier événement": ("modified", date_locale),
    "id": "id",
    "person_id": Coalesce(T.subscription.person_id.hex, T.person_id.hex, default=None),
    "email": "email",
    "nom": "last_name",
    "prenom": "first_name",
    "genre": Coalesce(T.subscription.meta["gender"], T.meta["gender"], default=None),
    "telephone": Coalesce("phone_number.as_international", default=None),
    "statut": T.get_status_display(),
    "montant": ("price", lambda m: Decimal(m) / 100),
    "type": "type",
    "mode": "mode",
    "abonnement associé": "subscription_id",
    "adresse1": Coalesce(T.subscription.meta["location_address1"], T.meta["location_address1"], default=None),
    "adresse2": Coalesce(T.subscription.meta["location_address2"], T.meta["location_address2"], default=None),
    "code postal": Coalesce(T.subscription.meta["location_zip"], T.meta["location_zip"], default=None),
    "ville": Coalesce(T.subscription.meta["location_city"],T.meta["location_city"], default=None),
    "pays": Coalesce(T.subscription.meta["location_country"], T.meta["location_country"], default=None),
    "nationality": Coalesce(T.subscription.meta["nationality"], T.meta["nationality"], default=None),
}


STATUS_MAPPING = {
    f[len("STATUS_") :]: getattr(Payment, f)
    for f in dir(Payment)
    if f.startswith("STATUS_") and f != "STATUS_CHOICES"
}


def statut_type(s):
    if s not in STATUS_MAPPING:
        tous_statuts = ", ".join(f"'{s}'" for s in STATUS_MAPPING)
        raise ArgumentTypeError(f"statut '{s}' inconnu (doit être un de {tous_statuts}")
    return STATUS_MAPPING[s]


def payment_type_type(s):
    if s not in PAYMENT_TYPES:
        tous_types = ", ".join(f"'{s}" for s in PAYMENT_TYPES)
        raise ArgumentTypeError(
            f"type de paiement '{s}' inconnu (doit être un de {tous_types})"
        )
    return s


def payment_mode_type(s):
    if s not in PAYMENT_MODES:
        tous_modes = ", ".join(f"'{s}" for s in PAYMENT_MODES)
        raise ArgumentTypeError(
            f"mode de paiement '{s}' inconnu (doit être un de {tous_modes})"
        )
    return s


MESSAGE_BODY = """
Bonjour,

Vous trouverez ci-joint l'export des paiements demandé.

Amitiés insoumises,
Action Populaire elle-même
"""


class Command(LoggingCommand):
    help = "Exporte les informations supplémentaires nécessaires pour l'audit des paiements"

    def add_arguments(self, parser):
        parser.add_argument(
            "--avant",
            type=datetime_argument,
            help="Limite l'extraction aux événements créés avant cette date",
        )
        parser.add_argument(
            "--apres",
            type=datetime_argument,
            help="Limite l'extraction aux événements créés après cette date",
        )

        parser.add_argument(
            "-t",
            "--type",
            dest="types",
            type=payment_type_type,
            action="append",
            metavar="TYPE",
            help="Limiter l'extraction à ce type de paiement. Répéter cette option permet d'inclure plusieurs types.",
        )

        parser.add_argument(
            "-m",
            "--mode",
            type=payment_mode_type,
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
            "--statut",
            type=statut_type,
            dest="statuts",
            action="append",
            help="Limiter aux paiements avec ce statut",
        )

        parser.add_argument(
            "-e",
            "--email",
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

    def handle(
        self, avant, apres, minimum, modes, types, statuts, emails, output, **kwargs
    ):
        condition = Q()

        if avant:
            condition &= Q(created__lte=avant)
        if apres:
            condition &= Q(created__gte=apres)
        if modes:
            condition &= Q(mode__in=modes)
        if types:
            condition &= Q(type__in=types)
        if minimum:
            condition &= Q(price__gte=minimum)
        if statuts:
            condition &= Q(status__in=statuts)

        payments = glom(
            Payment.objects.filter(condition).order_by("created"), [PAYMENT_SPEC]
        )

        logger.info(f"{len(payments)} correspondent aux critères demandés")

        logger.debug("Génération du fichier excel")
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
            logger.debug("Écriture du fichier excel")
            output.write(xlsx_content.getvalue())

        if emails:
            connection = get_connection()
            now = timezone.now().strftime("%Y-%m-%d-%H-%M")
            for e in emails:
                message = EmailMessage(
                    subject=f"Export des paiements",
                    body=MESSAGE_BODY,
                    from_email=settings.EMAIL_FROM_LFI,
                    to=[e],
                    connection=connection,
                )
                message.attach(
                    f"{now}-export-paiements.xlsx",
                    xlsx_content.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )

                logger.debug(f"Envoi de l'email à {e}")
                message.send()
