from datetime import timedelta

from django.contrib.gis.measure import D
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.management import BaseCommand
from django.db.models import Count, Case, When, BooleanField
from django.utils import timezone

from agir.people.models import Person
from agir.voting_proxies.actions import (
    get_voting_proxy_requests_for_proxy,
    PROXY_TO_REQUEST_DISTANCE_LIMIT,
)
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy
from agir.voting_proxies.tasks import (
    send_matching_request_to_voting_proxy,
    send_voting_proxy_candidate_invitation_email,
)


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

    def send_matching_requests_to_proxy(self, proxy, matching_request_ids):
        if self.dry_run:
            return

        proxy.last_matched = timezone.now()
        proxy.save()
        send_matching_request_to_voting_proxy.delay(
            proxy.id, list(matching_request_ids)
        )

    def invite_voting_proxy_candidates(self, candidates):
        if self.dry_run:
            return

        voting_proxy_candidates = [
            VotingProxy(
                status=VotingProxy.STATUS_INVITED,
                person=candidate,
                email=candidate.email,
                first_name=candidate.first_name if candidate.first_name else "-",
                last_name=candidate.last_name if candidate.first_name else "-",
                contact_phone=candidate.contact_phone if candidate.first_name else "-",
                polling_station_number="",
            )
            for candidate in candidates
        ]
        voting_proxy_candidates = VotingProxy.objects.bulk_create(
            voting_proxy_candidates, ignore_conflicts=True
        )
        send_voting_proxy_candidate_invitation_email.delay(
            [
                voting_proxy_candidate.pk
                for voting_proxy_candidate in voting_proxy_candidates
            ]
        )

    def find_voting_proxy_candidates_for_requests(self, pending_requests):
        possibly_fulfilled_request_ids = []
        candidate_ids = []

        # Find candidates for commune requests (up to 10 for each voter)
        for request in (
            pending_requests.exclude(commune__isnull=True)
            .values("email", "commune__mairie_localisation", "commune__code")
            .annotate(ids=ArrayAgg("id"))
        ):
            candidates = (
                Person.objects.exclude(
                    id__in=VotingProxy.objects.values_list("person_id", flat=True)
                )
                .exclude(id__in=candidate_ids)
                .exclude(coordinates__isnull=True)
                .exclude(emails__address=None)
                .exclude(emails__address=request["email"])
                .filter(is_2022=True, newsletters__len__gt=0)
            )

            # Match by distance for geolocalised communes
            if request["commune__mairie_localisation"]:
                candidates = candidates.filter(
                    coordinates__dwithin=(
                        request["commune__mairie_localisation"],
                        D(m=PROXY_TO_REQUEST_DISTANCE_LIMIT),
                    )
                )
            # Match by city code for non-geolocalised communes
            else:
                candidates = candidates.filter(
                    location_citycode=request["commune__code"]
                )

            # Give priority with people with the most rsvps and supportgroups
            candidates = (
                candidates.annotate(rsvp_count=Count("rsvps"))
                .annotate(supportgroup_count=Count("supportgroups"))
                .order_by("-rsvp_count", "-supportgroup_count")[:10]
            )

            if candidates.count() > 0:
                self.invite_voting_proxy_candidates(candidates)
                candidate_ids += candidates.values_list("id", flat=True)
                possibly_fulfilled_request_ids += request["ids"]

        return possibly_fulfilled_request_ids

    def match_available_proxies_with_requests(self, pending_requests):
        fulfilled_request_ids = []

        # Retrieve all available proxy that has not been matched in the last two days
        available_proxies = VotingProxy.objects.filter(
            status__in=(VotingProxy.STATUS_CREATED, VotingProxy.STATUS_AVAILABLE),
        ).exclude(last_matched__date__gt=timezone.now() - timedelta(days=2))

        # Try to match available voting proxies with pending requests
        for proxy in available_proxies:
            remaining_requests = pending_requests.exclude(id__in=fulfilled_request_ids)
            try:
                matching_request_ids = get_voting_proxy_requests_for_proxy(
                    proxy, remaining_requests
                ).values_list("id", flat=True)
            except VotingProxyRequest.DoesNotExist:
                pass
            else:
                self.send_matching_requests_to_proxy(proxy, matching_request_ids)
                fulfilled_request_ids += matching_request_ids

        return fulfilled_request_ids

    def handle(self, *args, dry_run=False, print_unfulfilled=False, **kwargs):
        self.dry_run = dry_run
        pending_requests = VotingProxyRequest.objects.filter(
            status=VotingProxyRequest.STATUS_CREATED,
            proxy__isnull=True,
        )
        self.stdout.write(
            f"\n\nTrying to fulfill {pending_requests.count()} pending requests..."
        )
        fulfilled_request_ids = self.match_available_proxies_with_requests(
            pending_requests
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
                f"\nLooking for voting proxy candidates for {pending_requests.count()} remaining requests..."
            )
            possibly_fulfilled_request_ids = (
                self.find_voting_proxy_candidates_for_requests(pending_requests)
            )
            if len(possibly_fulfilled_request_ids) > 0:
                pending_requests = pending_requests.exclude(
                    id__in=possibly_fulfilled_request_ids
                )
                self.stdout.write(
                    f" ☑ Voting proxy invitations sent for {len(possibly_fulfilled_request_ids)} pending requests"
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
