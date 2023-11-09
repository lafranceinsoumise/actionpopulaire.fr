from django.core.management import BaseCommand
from django.db import transaction

from agir.donations.allocations import (
    get_account_name_for_departement,
    get_departement_balance,
    get_account_name_for_group,
)
from agir.donations.models import AccountOperation
from agir.groups.models import SupportGroup


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--comment",
            default="Versement mensuel aux boucles départementales.",
        )

    def handle(self, *args, comment, **options):
        boucles = SupportGroup.objects.filter(
            type=SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE,
        ).exclude(location_departement_id="")

        with transaction.atomic():
            for b in boucles:
                balance = get_departement_balance(b.location_departement_id)

                if balance > 0:
                    AccountOperation.objects.create(
                        source=get_account_name_for_departement(
                            b.location_departement_id
                        ),
                        destination=get_account_name_for_group(b),
                        amount=balance,
                        comment=comment,
                    )
