from django.contrib.humanize.templatetags.humanize import apnumber
from django.core.management import BaseCommand
from django.utils import translation
from django.utils.translation import ngettext
from tqdm import tqdm

from agir.event_requests.actions import create_event_request_from_personform_submission
from agir.event_requests.models import EventRequest
from agir.people.person_forms.models import PersonFormSubmission


class Command(BaseCommand):
    """
    Create event request instances from one or more person form submission
    """

    help = "Create event request instances from one or more person form submission"

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.tqdm = None
        self.dry_run = None
        self.silent = False
        self.unique = False

    def execute(self, *args, **options):
        default_language = translation.get_language()
        translation.activate("en")
        self.log("\n")
        output = super().execute(*args, **options)
        translation.activate(default_language)
        self.log("\n👋 Bye!\n\n")
        return output

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
        parser.add_argument(
            "-u",
            "--unique",
            dest="unique",
            action="store_true",
            default=False,
            help="Do not create an event request if another one already exists for the same person form submission",
        )
        parser.add_argument(
            "submission_ids",
            nargs="*",
            type=int,
            help="Limit event request selection to the specified ids",
        )

    def log(self, message):
        if self.silent:
            return
        if self.tqdm:
            self.tqdm.clear()
        if not isinstance(message, str):
            message = str(message)
        self.stdout.write(message)

    def info(self, message):
        self.log(self.style.MIGRATE_HEADING(f"{message}"))

    def warning(self, message):
        self.log(self.style.WARNING(f"⚠ {message}"))

    def success(self, message):
        if self.dry_run:
            message = "[DRY-RUN] " + message
        self.log(self.style.SUCCESS(f"✔ {message}"))

    def error(self, message):
        if self.dry_run:
            message = "[DRY-RUN] " + message
        self.log(self.style.ERROR(f"✖ {message}"))

    def log_current_item(self, item):
        self.tqdm.set_description_str(str(item))

    def create_event_request_from_personform_submission(self, submission_id):
        self.tqdm.update(1)
        self.log_current_item(f"{submission_id}")

        submission_has_event_request = EventRequest.objects.filter(
            event_data__from_personform_submission_id=submission_id
        ).exists()

        if submission_has_event_request and self.unique:
            self.error(
                f"No event request will be created since one already exists "
                f"for this submission id: {submission_id}."
            )
            return None

        if submission_has_event_request:
            self.warning(
                f"An event request already exists for this submission id: {submission_id}"
            )

        try:
            return create_event_request_from_personform_submission(
                submission_id, do_not_create=self.dry_run
            )
        except PersonFormSubmission.DoesNotExist:
            self.error(f"No person form submission found for id: {submission_id}")
            return None

    def handle(
        self,
        *args,
        dry_run=False,
        silent=False,
        unique=False,
        submission_ids=None,
        **kwargs,
    ):
        self.dry_run = dry_run
        self.silent = silent
        self.unique = unique

        if submission_ids is None:
            submission_ids = []

        submission_ids = set(submission_ids)
        submission_count = len(submission_ids)

        if submission_count == 0:
            self.error("The following required arguments are missing: submission_id")
            return

        self.info(
            ngettext(
                f"⌛ One person form submission found. Creating event request objects...",
                f"⌛ {str(apnumber(submission_count)).capitalize()} person form submissions found. "
                f"Creating event request objects...",
                submission_count,
            )
        )

        self.tqdm = tqdm(
            total=submission_count,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
            disable=silent or submission_count == 1,
            colour="#cbbfec",
        )

        event_requests = [
            event_request
            for event_request in [
                self.create_event_request_from_personform_submission(submission_id)
                for submission_id in submission_ids
            ]
            if event_request is not None
        ]

        self.log_current_item("")
        self.tqdm.close()

        event_request_count = len(event_requests)

        if event_request_count == 0:
            self.error("No event request created.")
            return

        self.success(
            ngettext(
                f"One event request has been created.",
                f"{str(apnumber(event_request_count)).capitalize()} event requests have been created.",
                event_request_count,
            )
        )

        return
