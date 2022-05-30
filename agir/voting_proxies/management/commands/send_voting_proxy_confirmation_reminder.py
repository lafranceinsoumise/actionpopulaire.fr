from django.contrib.postgres.aggregates import ArrayAgg
from django.core.management import BaseCommand
from tqdm import tqdm

from agir.voting_proxies.models import VotingProxyRequest
from agir.voting_proxies.tasks import send_voting_proxy_request_confirmation_reminder


class Command(BaseCommand):
    """
    Send reminder for non-confirmed accepted voting proxy requests
    """

    help = "Send reminder for non-confirmed accepted voting proxy requests"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.tqdm = None
        self.dry_run = None

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            default=False,
            help="Execute without actually sending any notification or updating data",
        )
        parser.add_argument(
            "-s",
            "--silent",
            dest="silent",
            action="store_true",
            default=False,
            help="Display a progress bar during the script execution",
        )

    def log(self, message):
        self.tqdm.write(message)

    def send_reminder(self, request):
        if self.dry_run:
            return
        send_voting_proxy_request_confirmation_reminder.delay(request["ids"])

    def handle(
        self,
        *args,
        dry_run=False,
        silent=False,
        **kwargs,
    ):
        self.dry_run = dry_run
        requests = (
            VotingProxyRequest.objects.waiting_confirmation()
            .values("email")
            .annotate(ids=ArrayAgg("id"))
        )
        self.tqdm = tqdm(
            total=len(requests),
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
            disable=silent,
        )
        self.log(f"Sending {len(requests)} confirmation reminders ")
        for request in requests:
            self.send_reminder(request)
            self.tqdm.update(1)

        self.log("\nBye!\n\n")
        self.tqdm.close()
