from datetime import timedelta

from django.contrib.humanize.templatetags.humanize import apnumber
from django.utils import timezone
from django.utils.translation import ngettext

from agir.groups import tasks
from agir.groups.proxys import UncertifiableGroup
from agir.lib.commands import BaseCommand


class Command(BaseCommand):
    """
    Retrieve uncertifiable supportgroups and :
    - send warnings to group referents if none have been sent since certification date
    - send the list of groups that have received a warning more than one month ago to the admin email
    """

    help = """
        Retrieve uncertifiable supportgroups and :
        - send warnings to group referents if none have been sent since certification date
        - send the list of groups that have received a warning more than one month ago to the admin email
        """

    WARNING_EXPIRATION_IN_DAYS = 31

    def warn_uncertifiable_group_referents(self, group):
        if not self.dry_run:
            tasks.send_uncertifiable_group_warning.delay(
                group.id, self.WARNING_EXPIRATION_IN_DAYS
            )

    def send_uncertifiable_group_list(self, group_ids):
        if not self.dry_run:
            tasks.send_uncertifiable_group_list.delay(
                group_ids, self.WARNING_EXPIRATION_IN_DAYS
            )

    def check_uncertifiable_groups(self, uncertifiable_groups):
        warned = []
        uncertifiable = []

        for group in uncertifiable_groups:
            self.log_current_item(f"{group}")
            self.tqdm.update(1)

            # Warning has not been sent yet
            if group.uncertifiable_warning_date is None:
                self.warn_uncertifiable_group_referents(group)
                warned.append(group.id)
                continue

            # Warning has been sent less than 31 days ago
            if timezone.now() <= group.uncertifiable_warning_date + timedelta(
                days=self.WARNING_EXPIRATION_IN_DAYS
            ):
                continue

            # Warning has expired
            uncertifiable.append((group.id, group.uncertifiable_warning_date))

        if uncertifiable:
            uncertifiable = sorted(uncertifiable, key=lambda i: i[1])
            uncertifiable = [group_id for group_id, _date in uncertifiable]
            self.send_uncertifiable_group_list(uncertifiable)

        return len(warned), len(uncertifiable)

    def handle(
        self,
        *args,
        **kwargs,
    ):
        uncertifiable_groups = UncertifiableGroup.objects.prefetch_related(
            "notifications"
        ).only("id", "name")
        uncertifiable_group_count = len(uncertifiable_groups)

        if uncertifiable_group_count == 0:
            self.error("No uncertifiable group found.")
            return

        self.init_tqdm(total=uncertifiable_group_count)

        self.info(
            ngettext(
                f"⌛ One uncertifiable group found.",
                f"⌛ {str(apnumber(uncertifiable_group_count)).capitalize()} uncertifiable groups found.",
                uncertifiable_group_count,
            )
        )

        warned, uncertifiable = self.check_uncertifiable_groups(uncertifiable_groups)

        self.log_current_item("")
        self.tqdm.close()

        if warned == 0:
            self.success("No warning has been sent.")
        else:
            self.success(
                ngettext(
                    f"One warning has been sent.",
                    f"{str(apnumber(warned)).capitalize()} warning have been sent",
                    warned,
                )
            )

        if uncertifiable == 0:
            self.success("No uncertifiable group have been found")
        else:
            self.success(
                ngettext(
                    f"One uncertifiable group have been found and sent to the admin.",
                    f"{str(apnumber(uncertifiable)).capitalize()} uncertifiable groups have been found and sent to the admin.",
                    uncertifiable,
                )
            )
