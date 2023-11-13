import re

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
        )

        with transaction.atomic():
            for b in boucles:
                if b.location_departement_id:
                    code = b.location_departement_id
                else:
                    num = re.search("\d+", b.name).group(0).zfill(2)
                    code = f"99-{num}"

                balance = get_departement_balance(code)

                if balance > 0:
                    AccountOperation.objects.create(
                        source=get_account_name_for_departement(code),
                        destination=get_account_name_for_group(b),
                        amount=balance,
                        comment=comment,
                    )
