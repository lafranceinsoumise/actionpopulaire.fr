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
from agir.events.tasks import geocode_event
from agir.gestion.models import Projet
from agir.gestion.typologies import TypeProjet
from agir.groups.models import SupportGroup
from agir.lib.management_utils import LoggingCommand
from agir.people.person_forms.display import default_person_form_display
from agir.people.person_forms.models import PersonForm


logger = logging.getLogger(__name__)


DESCRIPTION_TEMPLATE = """
Demande de réunion publique via le formulaire.

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
        reunion_publique = EventSubtype.objects.get(label="reunion-publique")
        submissions = form.submissions.annotate(
            projet_cree=Exists(
                Projet.objects.annotate(
                    submission_id=Cast(
                        Func(
                            F("details"),
                            Value("submission_id"),
                            function="jsonb_extract_path_text",
                        ),
                        output_field=IntegerField(),
                    )
                ).filter(submission_id=OuterRef("id"))
            ),
            possible_date=Cast(
                Func(
                    F("data"),
                    Value("possible_date"),
                    function="jsonb_extract_path_text",
                ),
                output_field=DateTimeField(),
            ),
        ).filter(projet_cree=False, possible_date__gt=now)

        logger.info(f"Création de {submissions.count()} nouveaux projets")
        # créer les projets correspondants
        for s in submissions.filter(projet_cree=False):
            name = f'Réunion publique à {s.data["location_city"]}'
            date = parse_date(s.data["possible_date"])

            if s.data.get("organizer_group"):
                try:
                    group = SupportGroup.objects.get(id=s.data["organizer_group"])
                except SupportGroup.DoesNotExist:
                    group = None
            else:
                group = None

            logger.debug(f"Création projet et événement « {name} »")

            with transaction.atomic():
                event = Event.objects.create(
                    name=name[: Event._meta.get_field("name").max_length],
                    visibility=Event.VISIBILITY_ORGANIZER,
                    subtype=reunion_publique,
                    start_time=date,
                    end_time=date + timedelta(hours=2),
                    **{
                        k: v[: Event._meta.get_field(k).max_length]
                        for k, v in s.data.items()
                        if k
                        in [
                            "location_name",
                            "location_address1",
                            "location_zip",
                            "location_city",
                        ]
                    },
                )

                OrganizerConfig.objects.create(
                    event=event, person=s.person, as_group=group
                )

                Projet.objects.create(
                    titre=name[: Projet._meta.get_field("titre").max_length],
                    event=event,
                    type=TypeProjet.REUNION_PUBLIQUE_ORATEUR,
                    origine=Projet.Origin.REUNION_PUBLIQUE,
                    etat=Projet.Etat.CREE_PLATEFORME,
                    description=description_from_submission(s),
                    details={"submission_id": s.id},
                )

            geocode_event.delay(event.pk)
