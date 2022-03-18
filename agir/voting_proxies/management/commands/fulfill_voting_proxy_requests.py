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
from agir.voting_proxies.tasks import send_matching_report_email


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
        self.report = {
            "datetime": timezone.now().isoformat(),
            "dry-run": False,
            "pending_request_count": 0,
            "matched_request_count": 0,
            "pending_requests": {},
            "matched_proxies": [],
            "invitations": [],
        }

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

    def report_pending_requests(self, pending_requests):
        self.report["pending_request_count"] = pending_requests.count()
        self.report["pending_requests"] = {
            str(request.id): {
                "id": str(request.id),
                "created": request.created.isoformat(),
                "date": request.voting_date.isoformat(),
                "email": request.email,
                "commune": request.commune.nom if request.commune else None,
                "consulate": request.consulate.nom if request.consulate else None,
            }
            for request in pending_requests
        }

    def report_matched_proxy(self, proxy, matching_request_ids):
        for vpr in matching_request_ids:
            vpr = str(vpr)

            if vpr not in self.report["pending_requests"]:
                self.report["pending_requests"][vpr] = {"id": vpr}

            self.report["pending_requests"][vpr]["matched_proxy"] = {
                "id": str(proxy.id),
                "email": proxy.email,
            }

        self.report["matched_proxies"].append(
            {
                "id": str(proxy.id),
                "email": proxy.email,
                "vpr": [str(vpr) for vpr in matching_request_ids],
            }
        )

    def report_invitation(self, candidates, request):
        for vpr in request["ids"]:
            vpr = str(vpr)

            if vpr not in self.report["pending_requests"]:
                self.report["pending_requests"][vpr] = {"id": vpr}

            self.report["pending_requests"][str(vpr)]["candidate_proxies"] = [
                c.email for c in candidates
            ]

        self.report["invitations"].append(
            {
                "from": request["email"],
                "to": [c.email for c in candidates],
                "vpr": [str(vpr) for vpr in request["ids"]],
            }
        )

    def send_matching_requests_to_proxy(self, proxy, matching_request_ids):
        self.report_matched_proxy(proxy, matching_request_ids)

        if self.dry_run:
            return

        send_matching_requests_to_proxy(proxy, matching_request_ids)

    def invite_voting_proxy_candidates(self, candidates, request):
        self.report_invitation(candidates, request)

        if self.dry_run:
            return candidates.values_list("id", flat=True)

        return invite_voting_proxy_candidates(candidates, request)

    def log(self, message):
        self.stdout.write(message)

    def send_report(self):
        self.report["dry_run"] = self.dry_run
        send_matching_report_email.delay(self.report)

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
        self.report_pending_requests(pending_requests)
        self.log(
            f"\n\nTrying to fulfill {pending_requests.count()} pending requests..."
        )

        fulfilled_request_ids = match_available_proxies_with_requests(
            pending_requests, notify_proxy=self.send_matching_requests_to_proxy
        )
        self.report["matched_request_count"] = len(fulfilled_request_ids)
        if len(fulfilled_request_ids) > 0:
            pending_requests = pending_requests.exclude(id__in=fulfilled_request_ids)
            self.log(
                f" ☑ Available voting proxies found for {len(fulfilled_request_ids)} pending requests."
            )
        else:
            self.log(f" ☒ No available voting proxy found :-(")

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
                self.log(f"\nToday is an {'odd' if is_an_odd_day else 'even'} day!")

            self.log(
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
                self.log(
                    f" ☑ {len(candidate_ids)} voting proxy invitation(s) sent "
                    f"for {len(possibly_fulfilled_request_ids)} pending requests"
                )
            else:
                self.log(f" ☒ No voting proxy candidate found :-(")

        if pending_requests.count() > 0:
            self.log(f"\n{pending_requests.count()} unfulfilled requests remaining\n")
            if print_unfulfilled:
                # Print remaining unfulfilled requests
                for pending_request in pending_requests:
                    self.log(
                        f" — {pending_request}, "
                        f"{pending_request.commune if pending_request.commune else pending_request.consulate}\n"
                    )
            self.log("\n")
        else:
            self.log(f"\nNo unfulfilled requests remaining for today!")

        self.send_report()
        self.log("Bye!\n\n")
