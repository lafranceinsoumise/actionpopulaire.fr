from django.core.management import BaseCommand

from agir.groups.tasks import (
    maj_boucles_departementales,
)
from agir.lib.data import departements_par_code


class Command(BaseCommand):
    help = "Automatically add/update/remove `boucles departementales`-type supportgroup members"
    dry_run = False
    silent = False

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--departements",
            dest="only_departements",
            default=None,
            help=f"Limit to some departements based on a list of comma separated codes "
            f"(ex. -d 01,02,03)",
        )
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            default=False,
            help="Execute and print output without actually creating any member",
        )
        parser.add_argument(
            "-s",
            "--silent",
            dest="silent",
            action="store_true",
            default=False,
            help="Execute without printing any output",
        )

    def log(self, message):
        if not self.silent:
            print(message)

    def print_result(self, result):
        if not result:
            return
        for departement, count in result:
            if count is None:
                self.log(
                    f"✖ Département {departement.id} — {departement.nom} : pas de boucle départementale"
                )
                continue
            existing, created, deleted = count
            self.log(
                f"✔ Département {departement.id} — {departement.nom} : boucle départementale mise à jour"
            )
            if self.dry_run:
                self.log(f"  ├── Membres existants : {existing}")
                self.log(f"  ├── Membres à supprimer : {deleted}")
                self.log(f"  └── Membres à ajouter : {created}")
            else:
                self.log(f"  ├── Membres existants : {existing}")
                self.log(f"  ├── Membres supprimés : {deleted}")
                self.log(f"  └── Membres ajoutés : {created}")

    def handle(
        self,
        *args,
        only_departements=None,
        dry_run=False,
        silent=False,
        **kwargs,
    ):
        self.dry_run = dry_run
        self.silent = silent

        if only_departements:
            only_departements = [
                departements_par_code[code]
                for code in sorted(set(only_departements.split(",")))
                if code in departements_par_code.keys()
            ]

        if only_departements is None:
            self.log(
                "\nMise à jour des boucles départementales de tous les départements\n"
            )
            result = maj_boucles_departementales(
                only_departements=None, dry_run=dry_run
            )
            self.print_result(result)
            self.log("\nBye!\n\n")
            return

        if only_departements:
            self.log(
                "\nMise à jour des boucles départementales des départements suivants :"
            )
            self.log(f"✹✹✹ {','.join(str(d) for d in only_departements)}\n")
            result = maj_boucles_departementales(
                only_departements=only_departements, dry_run=dry_run
            )
            self.print_result(result)
            self.log("\nBye!\n\n")
            return

        self.log("\nAucun département trouvé pour les codes spécifiés !")
        self.log("\nBye!\n\n")
