import argparse
import math
import re

import pandas as pd
from django.core.management import BaseCommand

from agir.donations.allocations import (
    COTISATIONS_ACCOUNT,
    get_account_name_for_departement,
    CNS_ACCOUNT,
)
from agir.donations.models import AccountOperation


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "cotisations",
            type=argparse.FileType("rb"),
        )

        parser.add_argument(
            "-p",
            "--part-cns",
            dest="part_cns",
            default=0.2,
            type=float,
        )

        parser.add_argument(
            "-c",
            "--comment",
            default="Versement des cotisations d'élus",
        )

    def handle(self, cotisations, part_cns, comment, **kwargs):
        df = pd.read_excel(
            cotisations,
        )
        df.columns = ["departement", "montant"]
        df["departement"] = df.departement.map(str).str.zfill(2).str.upper()
        df["montant"] = (df["montant"] * 100).round().astype(int)

        versements = df.set_index("departement")["montant"].to_dict()

        deps = [
            d
            for d, v in versements.items()
            if re.match(r"^(?:\d[0-9AB]|9[78]\d)$", d) and v
        ]
        cns = versements.pop("CNS", 0.0)

        if part_cns:
            for d in deps:
                cns += math.ceil(versements[d] * part_cns)
                versements[d] = math.floor(versements[d] * (1 - part_cns))

        for d in deps:
            AccountOperation.objects.create(
                source=COTISATIONS_ACCOUNT,
                destination=get_account_name_for_departement(d),
                amount=versements[d],
                comment=comment,
            )

        if cns:
            AccountOperation.objects.create(
                source=COTISATIONS_ACCOUNT,
                destination=CNS_ACCOUNT,
                amount=cns,
                comment=comment,
            )
