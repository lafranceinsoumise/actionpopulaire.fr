import re

from django.core.management import BaseCommand
from django.utils.translation import ngettext

from agir.groups.actions.automatic_memberships import (
    refresh_supportgroups_with_membership_segment,
)
from agir.groups.models import SupportGroup


class Command(BaseCommand):
    help = "Automatically add/update/remove members for supportgroup that have a membership segment"
    dry_run = False
    silent = False

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def add_arguments(self, parser):
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

        for group, count in result.items():
            if count is None:
                continue
            existing, created, deleted = count
            self.log(f"✔ {group.name} : groupe mis à jour")

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
        dry_run=False,
        silent=False,
        **kwargs,
    ):
        self.dry_run = dry_run
        self.silent = silent

        supportgroups = (
            SupportGroup.objects.active()
            .exclude(type=SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE)
            .filter(membership_segment__isnull=False)
            .select_related("membership_segment")
        )
        count = supportgroups.count()

        if count == "0":
            self.log("Aucun groupe avec un segment d'adhésion n'a été trouvé.")
            return

        self.log(
            ngettext(
                "\nMise à jour d'un groupe avec un segment d'adhésion\n",
                f"\nMise à jour de {count} groupes avec un segment d'adhésion\n",
                count,
            )
        )

        result = refresh_supportgroups_with_membership_segment(
            supportgroups, dry_run=dry_run
        )

        self.print_result(result)
        self.log("\nBye!\n\n")
