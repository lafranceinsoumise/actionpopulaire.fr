from django.utils import timezone

from agir.lib.commands import BaseCommand
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
            "-o",
            "--one-round",
            dest="one_round_election",
            action="store_true",
            default=False,
            help="Improve distance matching algorithm for one round elections",
        )
        super().add_arguments(parser)

    def report_pending_requests(self, pending_requests):
        self.report["pending_requests"] = {
            str(request.id): {
                "id": str(request.id),
                "created": request.created.isoformat(),
                "date": request.voting_date.isoformat(),
                "email": request.email,
                "commune": request.commune.nom if request.commune else None,
                "consulate": request.consulate.nom if request.consulate else None,
            }
            for request in pending_requests.select_related("commune", "consulate")
        }

    def report_matched_proxy(self, proxy, matching_request_ids):
        self.tqdm.update(len(matching_request_ids))
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
        self.tqdm.update(len(request["ids"]))
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

    def send_report(self):
        self.report["dry_run"] = self.dry_run
        send_matching_report_email.delay(self.report)

    def handle(
        self,
        *args,
        one_round_election=False,
        **kwargs,
    ):
        pending_requests = VotingProxyRequest.objects.pending()
        initial_request_count = len(pending_requests)
        self.init_tqdm(initial_request_count)
        self.report["pending_request_count"] = initial_request_count
        self.report_pending_requests(pending_requests)
        self.info(f"\nTrying to fulfill {initial_request_count} pending requests...")
        fulfilled_request_ids = match_available_proxies_with_requests(
            pending_requests,
            notify_proxy=self.send_matching_requests_to_proxy,
            one_round_election=one_round_election,
        )
        self.report["matched_request_count"] = len(fulfilled_request_ids)
        if len(fulfilled_request_ids) > 0:
            pending_requests = pending_requests.exclude(id__in=fulfilled_request_ids)
            self.success(
                f"Available voting proxies found for {len(fulfilled_request_ids)} pending requests."
            )
        else:
            self.error(f"No available voting proxy found :-(")

        unfulfilled_request_count = len(pending_requests)
        if unfulfilled_request_count > 0:
            self.info(
                f"\nLooking for voting proxy candidates for {unfulfilled_request_count} requests..."
            )
            (
                possibly_fulfilled_request_ids,
                candidate_ids,
            ) = find_voting_proxy_candidates_for_requests(
                pending_requests,
                send_invitations=self.invite_voting_proxy_candidates,
            )
            if len(possibly_fulfilled_request_ids) > 0:
                pending_requests.exclude(id__in=possibly_fulfilled_request_ids)
                unfulfilled_request_count -= len(possibly_fulfilled_request_ids)
                self.success(
                    f" ☑ {len(candidate_ids)} voting proxy invitation(s) sent "
                    f"for {len(possibly_fulfilled_request_ids)} pending requests"
                )
            else:
                self.error(f"No voting proxy candidate found :-(")

        if unfulfilled_request_count > 0:
            self.info(f"\n{unfulfilled_request_count} unfulfilled requests remaining")
        else:
            self.info(f"\nNo unfulfilled requests remaining for today!")

        self.tqdm.close()
        self.success("Sending script report")
        self.send_report()
