from django.core.management import BaseCommand

from agir.groups.tasks import send_soon_to_be_inactive_group_warning
from agir.groups.utils.supportgroup import (
    DAYS_SINCE_LAST_EVENT_WARNING,
    get_soon_to_be_inactive_groups,
)


class Command(BaseCommand):
    help = "Send warning emails to all soon-to-be-inactive groups"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)

    def add_arguments(self, parser):
        parser.add_argument(
            "-a",
            "--all",
            dest="all_groups",
            action="store_true",
            default=False,
            help=f"Send warnings to all soon-to-be-inactive groups. By default warnings will be sent only to groups "
            f"whose last event has started {DAYS_SINCE_LAST_EVENT_WARNING} days ago",
        )
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            default=False,
            help="Execute without actually sending any email",
        )

    def handle(
        self,
        *args,
        all_groups=False,
        dry_run=False,
        **kwargs,
    ):
        soon_to_be_inactive_groups = get_soon_to_be_inactive_groups(
            exact=not all_groups
        ).values_list("pk", flat=True)

        print("Sending warning emails to soon-to-be-inactive groups:")
        print(f"{len(soon_to_be_inactive_groups)} group(s) found")

        if dry_run is False:
            for group_pk in soon_to_be_inactive_groups:
                send_soon_to_be_inactive_group_warning.apply_async(args=(group_pk,))

        print("\nBye!\n\n")
