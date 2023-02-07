from django.contrib.humanize.templatetags.humanize import apnumber
from django.utils.translation import ngettext

from agir.event_requests.actions import create_event_request_from_personform_submission
from agir.lib.commands import BaseCommand
from agir.people.person_forms.models import PersonFormSubmission


class Command(BaseCommand):
    """
    Create event request instances from one or more person form submission
    """

    help = "Create event request instances from one or more person form submission"

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "personform_ids",
            nargs="*",
            type=int,
            help="Limit event request selection to the specified ids",
        )

    def create_event_request_from_personform_submission(self, submission):
        self.tqdm.update(1)
        self.log_current_item(f"{submission}")

        if submission.data.get("event_request_id", None):
            self.error(
                f"No event request will be created since one already exists "
                f"for this submission id: {submission.id}."
            )
            return None

        return create_event_request_from_personform_submission(
            submission, do_not_create=self.dry_run
        )

    def handle(
        self,
        *args,
        personform_ids=None,
        **kwargs,
    ):
        if personform_ids is None:
            personform_ids = []

        personform_ids = list(set(personform_ids))

        if len(personform_ids) == 0:
            self.error("You should specify at least one person form id")
            return

        submissions = PersonFormSubmission.objects.filter(
            form_id__in=personform_ids, data__event_request_id__isnull=True
        )
        submission_count = submissions.count()

        if submission_count == 0:
            self.error("No submission found for the specified form ids")
            return

        self.init_tqdm(total=submission_count)

        self.info(
            ngettext(
                f"⌛ One person form submission found. Creating event request objects...",
                f"⌛ {str(apnumber(submission_count)).capitalize()} person form submissions found. "
                f"Creating event request objects...",
                submission_count,
            )
        )

        event_requests = [
            event_request
            for event_request in [
                self.create_event_request_from_personform_submission(submissions)
                for submissions in submissions
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
