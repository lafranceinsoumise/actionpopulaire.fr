import logging
from datetime import timedelta

from django.db import transaction
from django.db.models import Func, F, Value, UUIDField, DateTimeField
from django.db.models.functions import Cast
from django.utils import timezone
from iso8601 import parse_date

from agir.events.models import Event, EventSubtype, OrganizerConfig
from agir.events.tasks import geocode_event
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
        parser.add_argument("event_subtype_label")
        parser.add_argument("-d", "--define", nargs=2, action="append")

    def handle(self, *args, form_slug, event_subtype_label, define, **options):
        command_values = dict(define or ())
        form = PersonForm.objects.get(slug=form_slug)
        event_subtype = EventSubtype.objects.get(label=event_subtype_label)
        submissions = form.submissions.annotate(
            evenement_existe=Cast(
                Func(
                    F("data"),
                    Value("_event_id"),
                    function="jsonb_extract_path_text",
                ),
                output_field=UUIDField(),
            ),
            start_time=Cast(
                Func(
                    F("data"),
                    Value("start_time"),
                    function="jsonb_extract_path_text",
                ),
                output_field=DateTimeField(),
            ),
        ).filter(evenement_existe__isnull=True, start_time__gte=timezone.now())

        logger.info(f"Création de {submissions.count()} nouveaux événements")
        # créer les projets correspondants
        for s in submissions:
            values = {**s.data, **command_values}

            name = values.pop("name", None)
            if not name:
                name = f"{event_subtype.description} à {values['location_city']}"

            start_time = parse_date(values.pop("start_time"))
            end_time = (
                parse_date(values.pop("end_time"))
                if values.get("end_time")
                else start_time + timedelta(hours=2)
            )

            organizer_group = None
            if "organizer_group" in values:
                organizer_group = SupportGroup.objects.filter(
                    id=s.data.pop("organizer_group")
                ).first()

            if values.pop("publish_contact_information", False):
                if "contact_name" not in values:
                    values["contact_name"] = (
                        f"{values.pop('first_name')} {values.pop('last_name')}"
                    )

                if "email" in values:
                    values["contact_email"] = values.pop("email")

                values["contact_hide_phone"] = False
            else:
                values["contact_hide_phone"] = True

            logger.debug(f"Création projet et événement « {name} »")

            with transaction.atomic():
                event = Event.objects.create(
                    organizer_person=s.person,
                    organizer_group=organizer_group,
                    name=name[: Event._meta.get_field("name").max_length],
                    visibility=Event.VISIBILITY_ADMIN,
                    subtype=event_subtype,
                    start_time=start_time,
                    end_time=end_time,
                    **{
                        k: v[: Event._meta.get_field(k).max_length]
                        for k, v in s.data.items()
                        if k
                        in [
                            "location_name",
                            "location_address1",
                            "location_zip",
                            "location_city",
                            "contact_name",
                            "contact_email",
                            "contact_phone",
                            "contact_hide_phone",
                        ]
                    },
                )

                s.data["_event_id"] = event.id
                s.save(update_fields=["data"])

            geocode_event.delay(event.pk)
