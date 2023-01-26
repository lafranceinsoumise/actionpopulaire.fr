from django.core.management import BaseCommand
from django.utils.translation import ngettext
from tqdm import tqdm

from agir.event_requests.models import EventSpeakerRequest, EventRequest


class Command(BaseCommand):
    """
    Try to fulfill pending event request by sending a notification for all available
    event speakers for each request theme, if not already notified
    """

    help = (
        "Try to fulfill pending event request by sending a notification for all available "
        "event speakers for each request theme, if not already notified"
    )

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.tqdm = None
        self.dry_run = None
        self.silent = False

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
        if self.silent:
            return
        if self.tqdm:
            self.tqdm.clear()
        self.stdout.write(f"{message}")

    def error(self, message):
        if self.silent:
            return
        if self.tqdm:
            self.tqdm.clear()
        self.stderr.write(f"{message}")

    def log_current_item(self, item):
        if self.silent:
            return
        self.tqdm.set_description_str(str(item))

    def create_event_speaker_requests(self, pending_event_requests):
        event_speaker_requests = []

        for event_request in pending_event_requests:
            self.tqdm.update(1)
            self.log_current_item(f"{event_request}")
            possible_event_speaker_ids = set(
                event_request.event_theme.event_speakers.available().values_list(
                    "id", flat=True
                )
            )
            if len(possible_event_speaker_ids) == 0:
                self.error(
                    f"⚠ No speaker found for the event request's theme: {event_request.event_theme.name}"
                )
                continue

            for datetime in event_request.datetimes:
                event_speaker_requests += [
                    EventSpeakerRequest(
                        event_request=event_request,
                        event_speaker_id=event_speaker_id,
                        datetime=datetime,
                    )
                    for event_speaker_id in possible_event_speaker_ids
                ]

        if self.dry_run:
            return [
                event_speaker_request
                for event_speaker_request in event_speaker_requests
                if not EventSpeakerRequest.objects.filter(
                    event_request=event_speaker_request.event_request,
                    event_speaker_id=event_speaker_request.event_speaker_id,
                    datetime=event_speaker_request.datetime,
                ).exists()
            ]

        return EventSpeakerRequest.objects.bulk_create(
            event_speaker_requests,
            ignore_conflicts=True,
            send_post_save_signal=True,
        )

    def notify_event_speakers(self, event_speaker_ids):
        for event_speaker_id in event_speaker_ids:
            # TODO: Actually schedule a task to send an email to the speaker
            if not self.dry_run:
                pass
            self.tqdm.update(1)

    def handle(
        self,
        *args,
        dry_run=False,
        silent=False,
        **kwargs,
    ):
        self.log("\n\n")
        self.dry_run = dry_run
        self.silent = silent
        pending_event_requests = EventRequest.objects.pending()
        pending_event_request_count = len(pending_event_requests)

        if pending_event_request_count == 0:
            self.log("✖ No pending event request found.")
            self.log("Bye!")
            return

        self.log(
            ngettext(
                f"⌛ Looking for speakers for one pending event request...",
                f"⌛ Looking for speakers {pending_event_request_count} pending event requests...",
                pending_event_request_count,
            )
        )

        self.tqdm = tqdm(
            total=pending_event_request_count,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
            disable=silent,
            colour="#cbbfec",
        )
        new_event_speaker_requests = self.create_event_speaker_requests(
            pending_event_requests
        )
        self.tqdm.close()
        self.log("\n")

        new_event_speaker_request_count = len(new_event_speaker_requests)
        if new_event_speaker_request_count == 0:
            self.log(
                "✖ No event speaker request created, no event speakers will be notified."
            )
            self.log("Bye!")
            return

        self.log(
            ngettext(
                f"✔ One event speaker request created.",
                f"✔ {new_event_speaker_request_count} event speaker requests created.",
                new_event_speaker_request_count,
            )
        )
        event_speaker_ids = set(
            [
                new_event_speaker_request.event_speaker_id
                for new_event_speaker_request in new_event_speaker_requests
            ]
        )
        event_speaker_count = len(event_speaker_ids)

        self.log(
            ngettext(
                f"⌛ Scheduling notification for {event_speaker_count} event speaker...",
                f"⌛ Scheduling notifications for {event_speaker_count} event speakers...",
                event_speaker_count,
            )
        )
        self.tqdm = tqdm(
            total=event_speaker_count,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
            disable=silent,
            colour="#fcfbd9",
        )
        self.notify_event_speakers(event_speaker_ids)
        self.tqdm.close()
        self.log("\n")
        self.log("✔ Done.")
        self.log("Bye!")
        self.log("\n\n")
