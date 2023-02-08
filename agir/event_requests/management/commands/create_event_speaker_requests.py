import uuid

from django.contrib.humanize.templatetags.humanize import apnumber
from django.utils.translation import ngettext

from agir.event_requests.models import EventSpeakerRequest, EventRequest
from agir.event_requests.tasks import send_new_event_speaker_request_notification
from agir.lib.commands import BaseCommand


class Command(BaseCommand):
    """
    Try to fulfill pending event request by sending a notification for all available
    event speakers for each request theme, if not already notified
    """

    help = (
        "Try to fulfill pending event request by sending a notification for all available "
        "event speakers for each request theme, if not already notified"
    )

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            "event_request_ids",
            nargs="*",
            type=uuid.UUID,
            help="Limit event request selection to the specified ids",
        )

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
                self.warning(
                    f"No speaker found for the event request's theme: “{event_request.event_theme.name}”"
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
            if not self.dry_run:
                send_new_event_speaker_request_notification.delay(event_speaker_id)
            self.tqdm.update(1)

    def handle(
        self,
        *args,
        event_request_ids=None,
        **kwargs,
    ):
        pending_event_requests = EventRequest.objects.pending()
        if event_request_ids:
            pending_event_requests = pending_event_requests.filter(
                id__in=event_request_ids
            )
        pending_event_request_count = len(pending_event_requests)

        if pending_event_request_count == 0:
            self.error("No pending event request found.")
            return

        self.init_tqdm(total=pending_event_request_count)
        self.info(
            ngettext(
                f"⌛ One pending event request found. Looking for speakers...",
                f"⌛ {str(apnumber(pending_event_request_count)).capitalize()} pending event requests found. "
                f"Looking for speakers...",
                pending_event_request_count,
            )
        )

        new_event_speaker_requests = self.create_event_speaker_requests(
            pending_event_requests
        )
        self.log_current_item("")
        self.tqdm.close()

        new_event_speaker_request_count = len(new_event_speaker_requests)
        if new_event_speaker_request_count == 0:
            self.error(
                "No event speaker request created : no event speaker will be notified."
            )
            return

        self.success(
            ngettext(
                f"One event speaker request has been created.",
                f"{str(apnumber(new_event_speaker_request_count)).capitalize()} event speaker requests have been created.",
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

        self.log("\n")
        self.init_tqdm(total=event_speaker_count)
        self.info(
            ngettext(
                f"⌛ Scheduling notification to one event speaker...",
                f"⌛ Scheduling notifications to {apnumber(event_speaker_count)} event speakers...",
                event_speaker_count,
            )
        )
        self.notify_event_speakers(event_speaker_ids)
        self.log_current_item("")
        self.tqdm.close()
        self.success(
            ngettext(
                f"One notification has been scheduled.",
                f"{str(apnumber(event_speaker_count)).capitalize()} notifications have been scheduled.",
                event_speaker_count,
            )
        )
