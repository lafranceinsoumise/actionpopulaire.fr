from django.core.management import BaseCommand
from django.db.models import Case, When, BooleanField
from django.utils import timezone

from agir.voting_proxies.actions import (
    send_matching_requests_to_proxy,
    match_available_proxies_with_requests,
    invite_voting_proxy_candidates,
    find_voting_proxy_candidates_for_requests,
)
from agir.voting_proxies.models import VotingProxyRequest


class Command(BaseCommand):
    """
    Try to fulfill pending voting proxy request either by sending an invitation to existing voting proxies or
    by inviting candidate AP users to join the voting proxy poll
    """

    help = (
        "Try to fulfill pending voting proxy request either by sending an invitation to existing voting proxies or"
        "by inviting candidate AP users to become voting proxies"
    )

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
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
            "-p",
            "--print-unfulfilled",
            dest="print_unfulfilled",
            action="store_true",
            default=False,
            help="Print unfulfilled requests at the end of the script",
        )
        parser.add_argument(
            "-na",
            "--do-not-alternate",
            dest="do_not_alternate",
            action="store_true",
            default=False,
            help="Do not alternate between odd/even days for proxy invitations",
        )

    def send_matching_requests_to_proxy(self, proxy, matching_request_ids):
        if self.dry_run:
            return

        send_matching_requests_to_proxy(proxy, matching_request_ids)

    def invite_voting_proxy_candidates(self, candidates):
        if self.dry_run:
            return candidates.values_list("id", flat=True)

        return invite_voting_proxy_candidates(candidates)

    def handle(
        self,
        *args,
        dry_run=False,
        print_unfulfilled=False,
        do_not_alternate=False,
        **kwargs,
    ):
        self.dry_run = dry_run
        pending_requests = VotingProxyRequest.objects.filter(
            status=VotingProxyRequest.STATUS_CREATED,
            proxy__isnull=True,
        )
        self.stdout.write(
            f"\n\nTrying to fulfill {pending_requests.count()} pending requests..."
        )
        fulfilled_request_ids = match_available_proxies_with_requests(
            pending_requests, notify_proxy=self.send_matching_requests_to_proxy
        )

        if len(fulfilled_request_ids) > 0:
            pending_requests = pending_requests.exclude(id__in=fulfilled_request_ids)
            self.stdout.write(
                f" ☑ Available voting proxies found for {len(fulfilled_request_ids)} pending requests."
            )
        else:
            self.stdout.write(f" ☒ No available voting proxy found :-(")

        # Invite AP users to join the voting proxy pool for the remaining requests
        if pending_requests.count() > 0:
            if not do_not_alternate:
                # Alternate sending of candidate invitations to leave past recipients
                # at least one day to reply
                is_an_odd_day = (timezone.now().day % 2) > 0
                pending_requests = pending_requests.annotate(
                    is_odd=Case(
                        When(created__day__iregex="[13579]$", then=True),
                        default=False,
                        output_field=BooleanField(),
                    )
                ).filter(is_odd=is_an_odd_day)
                self.stdout.write(
                    f"\nToday is an {'odd' if is_an_odd_day else 'even'} day!"
                )

            self.stdout.write(
                f"\nLooking for voting proxy candidates for {pending_requests.count()} remaining requests..."
            )
            (
                possibly_fulfilled_request_ids,
                candidate_ids,
            ) = find_voting_proxy_candidates_for_requests(
                pending_requests, send_invitations=self.invite_voting_proxy_candidates
            )
            if len(possibly_fulfilled_request_ids) > 0:
                pending_requests = pending_requests.exclude(
                    id__in=possibly_fulfilled_request_ids
                )
                self.stdout.write(
                    f" ☑ {len(candidate_ids)} voting proxy invitation(s) sent "
                    f"for {len(possibly_fulfilled_request_ids)} pending requests"
                )
            else:
                self.stdout.write(f" ☒ No voting proxy candidate found :-(")

        if pending_requests.count() > 0:
            self.stdout.write(
                f"\n{pending_requests.count()} unfulfilled requests remaining\n"
            )
            if print_unfulfilled:
                # Print remaining unfulfilled requests
                for pending_request in pending_requests:
                    self.stdout.write(
                        f" — {pending_request}, "
                        f"{pending_request.commune if pending_request.commune else pending_request.consulate}\n"
                    )
            self.stdout.write("\n")
        else:
            self.stdout.write(f"\nNo unfulfilled requests remaining for today!")

        self.stdout.write("Bye!\n\n")
