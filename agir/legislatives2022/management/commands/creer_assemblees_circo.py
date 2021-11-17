import logging
from datetime import timedelta

from django.db import transaction
from django.db.models import (
    DateTimeField,
    Exists,
    OuterRef,
    Func,
    F,
    Value,
    IntegerField,
)
from django.db.models.functions import Cast
from django.utils import timezone
from iso8601 import parse_date

from agir.events.models import Event, EventSubtype, OrganizerConfig
from agir.groups.models import SupportGroup
from agir.lib.management_utils import LoggingCommand
from agir.people.person_forms.display import default_person_form_display
from agir.people.person_forms.models import PersonForm

logger = logging.getLogger(__name__)


DESCRIPTION_TEMPLATE = """
Organisation d'une assemblée de circonscription via le formulaire.

{data}
"""


def description_from_submission(s):
    fieldsets = default_person_form_display.get_formatted_submission(s)

    sections = "\n\n".join(
        [
            "{title}\n{sep}\n\n{champs}".format(
                title=fs["title"],
                sep="-" * len(fs["title"]),
                champs="\n".join(
                    "{label}: {value}".format(label=f["label"], value=f["value"])
                    for f in fs["data"]
                ),
            )
            for fs in fieldsets
        ]
    )

    return DESCRIPTION_TEMPLATE.format(data=sections)


class Command(LoggingCommand):
    def add_arguments(self, parser):
        parser.add_argument("form_slug")

    def handle(self, *args, form_slug, **options):
        now = timezone.now()
        form = PersonForm.objects.get(slug=form_slug)
        assemblee_circo = EventSubtype.objects.get(label="assemblee-circonscription")
        submissions = form.submissions.annotate(
            evenement_cree=Exists(
                Event.objects.annotate(
                    submission_id=Cast(
                        Func(
                            F("meta"),
                            Value("submission_id"),
                            function="jsonb_extract_path_text",
                        ),
                        output_field=IntegerField(),
                    )
                ).filter(submission_id=OuterRef("id"))
            ),
            possible_date=Cast(
                Func(F("data"), Value("date"), function="jsonb_extract_path_text",),
                output_field=DateTimeField(),
            ),
        ).filter(evenement_cree=False, possible_date__gt=now)

        logger.info(f"Création de {submissions.count()} nouveaux événements")
        # créer les projets correspondants
        for s in submissions:
            name = f'Assemblée de circonscription à {s.data["location_city"]}'
            date = parse_date(s.data["date"])

            try:
                group = SupportGroup.objects.get(id=s.data["premier_groupe"])
            except SupportGroup.DoesNotExist:
                group = None

            logger.debug(f"Création événement « {name} »")

            with transaction.atomic():
                event = Event.objects.create(
                    name=name,
                    visibility=Event.VISIBILITY_ORGANIZER,
                    subtype=assemblee_circo,
                    start_time=date,
                    end_time=date + timedelta(hours=3),
                    **{
                        k: v
                        for k, v in s.data.items()
                        if k
                        in [
                            "location_name",
                            "location_address1",
                            "location_zip",
                            "location_city",
                        ]
                    },
                    description=description_from_submission(s),
                    meta={"submission_id": s.id},
                )

                OrganizerConfig.objects.create(
                    event=event, person=s.person, as_group=group
                )
