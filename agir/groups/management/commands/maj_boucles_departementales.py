import re

from django.core.management import BaseCommand

from agir.groups.tasks import (
    maj_boucles,
)
from agir.lib.data import departements_par_code


CODE_RE = re.compile(
    r"^(?:99-(?:0[0-9]|1[01])|[01345678][0-9]|2[1-9AB]|9(?:[0-5]|7[1-8]|8[678]))$"
)


class Command(BaseCommand):
    help = "Automatically add/update/remove `boucles departementales`-type supportgroup members"
    dry_run = False
    silent = False

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--codes",
            dest="codes",
            default=None,
            help=f"Limiter à certaines boucles (code du département ou de la circonscription FE "
            f"(ex. -d 01,02,03,99-03)",
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
        for lieu, count in result.items():
            if count is None:
                self.log(f"✖ {lieu} : pas de boucle")
                continue
            existing, created, deleted = count
            self.log(f"✔ {lieu} : boucle mise à jour")
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
        codes=None,
        dry_run=False,
        silent=False,
        **kwargs,
    ):
        self.dry_run = dry_run
        self.silent = silent

        if codes:
            codes = codes.split(",")
            incorrects = [c for c in codes if not CODE_RE.match(c)]
            if incorrects:
                raise CommandError(
                    f"Les code suivants sont incorrects : {' ,'.join(incorrects)}"
                )

        if codes is None:
            self.log("\nMise à jour de toutes les boucles\n")
        else:
            self.log("\nMise à jour des boucles suivantes :")

        result = maj_boucles(codes=None, dry_run=dry_run)
        self.print_result(result)
        self.log("\nBye!\n\n")
