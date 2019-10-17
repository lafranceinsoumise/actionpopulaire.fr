import tablib as tablib
from django.core.management.base import BaseCommand
from django.utils import timezone
from glom import Coalesce, T, glom

from agir.lib.management_utils import month_argument, month_range
from agir.payments.models import Payment
from agir.system_pay.models import SystemPayTransaction

FILE_DESC = {
    "Code_uuid": (
        "systempaytransaction_set",
        T.get(status=SystemPayTransaction.STATUS_COMPLETED),
        "uuid",
        str,
    ),
    "No_abonnement": "subscription.id",
    "Email": "person.email",
    "Nom": Coalesce("person.last_name", "subscription.meta.last_name"),
    "Prénom": Coalesce(
        "person.first_name", "subscription.meta.first_name", skip=("",), default=""
    ),
    "No_et_Voie": Coalesce(
        "person.location_address1",
        "subscription.meta.first_name",
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
    "Pays": Coalesce(
        "person.location_country",
        "subscription.meta.location_country",
        skip=("",),
        default="",
    ),
    "Nationalité": "subscription.meta.nationality",
    "Téléphone": Coalesce(
        ("person.contact_phone", T.as_e164), "subscription.meta.contact_phone"
    ),
}


class Command(BaseCommand):
    help = "Exporte les informations supplémentaires nécessaires pour l'audit des dons réguliers"

    def add_arguments(self, parser):
        parser.add_argument("month", type=month_argument)

    def handle(self, *args, month, **options):
        if month is None:
            now = timezone.now()
            month = month_range(now.year, now.month)

        payments = (
            Payment.objects.filter(
                status=Payment.STATUS_COMPLETED,
                subscription__isnull=False,
                created__range=month,
            )
            .select_related("subscription", "person")
            .prefetch_related("systempaytransaction_set")
        )

        results = glom(payments, [FILE_DESC])

        s = tablib.Dataset(*(r.values() for r in results), headers=FILE_DESC.keys())
        self.stdout.buffer.write(s.export("xls"))
