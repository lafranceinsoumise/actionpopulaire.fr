from data_france.models import CirconscriptionConsulaire
from django.core.management import CommandError, BaseCommand
from django.db import transaction
from django.db.models import Q, Count, F

from agir.donations.allocations import (
    get_account_name_for_departement,
    CNS_ACCOUNT,
    get_cns_balance,
)
from agir.donations.models import AccountOperation
from agir.groups.models import SupportGroup
from agir.lib.geo import FRENCH_COUNTRY_CODES


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
            default="Attribution de la Caisse Nationale de Solidarité",
        )

    def handle(self, *args, allocation, comment, **options):
        with transaction.atomic():
            # on récupère le nombre de GA certifiés par département.
            q_certifies = Q(type=SupportGroup.TYPE_LOCAL_GROUP) & ~Q(
                certification_date=None
            )
            q_in_france = Q(location_country__in=["", *FRENCH_COUNTRY_CODES])

            nb_groupes_certifies_france = (
                SupportGroup.objects.filter(q_certifies & q_in_france)
                .order_by("location_departement_id")
                .values("location_departement_id")
                .annotate(c=Count("*"))
            )

            poids_france = {
                g["location_departement_id"]: g["c"]
                for g in nb_groupes_certifies_france
            }

            nb_groupes_certifies_etranger = (
                SupportGroup.objects.filter(q_certifies & ~q_in_france)
                .order_by("location_country")
                .values("location_country")
                .annotate(c=Count("*"))
            )

            correspondance_pays_circo = {
                p: c["circo"]
                for c in CirconscriptionConsulaire.objects.annotate(
                    circo=F("circonscription_legislative__code")
                ).values("pays", "circo")
                for p in c["pays"].split(",")
            }

            poids_circo_fe = {}
            for pays in nb_groupes_certifies_etranger:
                circo = correspondance_pays_circo[pays["location_country"]]
                poids_circo_fe[circo] = poids_circo_fe.get(circo, 0) + pays["c"]

            poids = {**poids_france, **poids_circo_fe}

            poids_total = sum(poids.values())

            cns = get_cns_balance()

            # seules les boucles de départements avec au moins un groupe certifié sont éligibles
            nb = len(poids)

            # on vérifie qu'il y a assez d'argent pour l'allocation initiale pour tous les départements
            if cns // allocation < nb:
                raise CommandError(
                    f"La balance de la caisse nationale de solidarité est insuffisante pour permettre le versement.\n"
                    f"Au maximum, l'allocation devrait être de {cns // nb} centimes."
                )

            remainder = cns - allocation * nb

            for d, p in poids.items():
                AccountOperation.objects.create(
                    # la résultat de la division entière est toujours inférieur au total
                    # au pire on laisse jusqu'à nb centimes dans la CNS
                    amount=allocation + p * remainder // poids_total,
                    source=CNS_ACCOUNT,
                    destination=get_account_name_for_departement(d),
                    comment=comment,
                )
