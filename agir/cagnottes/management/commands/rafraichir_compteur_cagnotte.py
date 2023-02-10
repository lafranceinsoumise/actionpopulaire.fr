from django.core.management import BaseCommand, CommandError

from agir.cagnottes.actions import rafraichir_compteur
from agir.cagnottes.models import Cagnotte


class Command(BaseCommand):
    help = "Recalcule le montant du compteur d'une cagnotte, au cas où celui-ci se soit désynchronisé"

    def add_arguments(self, parser):
        parser.add_argument(
            "slug", metavar="SLUG", help="Le slug de la cagnotte à recalculer"
        )

    def handle(self, *args, slug, **options):
        try:
            cagnotte = Cagnotte.objects.get(slug=slug)
        except Cagnotte.DoesNotExist:
            raise CommandError("aucune cagnotte avec ce slug n'existe !")

        self.stdout.write("Rafraîchissement en cours…", ending="")

        rafraichir_compteur(cagnotte)
        self.stdout.write(" OK !")
