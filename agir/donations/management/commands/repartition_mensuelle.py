from django.core.management import CommandError
from django.db import transaction
from django.db.models import Q, Count

from agir.donations.allocations import (
    get_account_name_for_departement,
    CNS_ACCOUNT,
    get_departement_balance,
    get_account_name_for_group,
    get_cns_balance,
)
from agir.donations.models import AccountOperation
from agir.groups.models import SupportGroup
from agir.lib.commands import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--allocation",
            default=8000,
            type=int,
        )

        parser.add_argument(
            "-c",
            "--comment",
            default="Versement mensuel",
        )

    def handle(self, *args, allocation, comment, **options):
        boucles = list(
            SupportGroup.objects.filter(
                type=SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE,
            ).exclude(location_departement_code="")
        )

        with transaction.atomic():
            cns = get_cns_balance()
            nb = len(boucles)

            # on vérifie qu'il y a assez d'argent pour l'allocation initiale pour tous les départements
            if cns // allocation < nb:
                raise CommandError(
                    f"La balance de la caisse nationale de solidarité est insuffisante pour permettre le versement.\n"
                    f"Au maximum, l'allocation devrait être de {cns // nb} centimes."
                )

            gs = (
                SupportGroup.objects.filter(
                    ~Q(certification_date=None)
                    & ~Q(location_departement_id="")
                    & Q(type=SupportGroup.TYPE_LOCAL_GROUP)
                )
                .order_by("location_departement_id")
                .values("location_departement_id")
                .annotate(c=Count("*"))
            )
            poids = {g["location_departement_id"]: g["c"] for g in gs}
            poids_total = sum(poids.values())

            for d, p in poids.items():
                AccountOperation.objects.create(
                    amount=(p * cns) // poids_total,
                    source=CNS_ACCOUNT,
                    destination=get_account_name_for_departement(d),
                    comment=comment,
                )

            for b in boucles:
                bal = get_departement_balance(b.location_departement_code)

                if bal > 0:
                    AccountOperation.objects.create(
                        amount=bal,
                        source=get_account_name_for_departement(
                            b.location_departement_code
                        ),
                        destination=get_account_name_for_group(b),
                        comment=comment,
                    )
