import json
from urllib.parse import urljoin

from django.conf import settings

from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse


from agir.people.models import Person


def get_all_fields(obj):
    return {
        str(f.verbose_name): getattr(obj, f.name)
        for f in obj._meta.get_fields()
        if not f.is_relation
    }


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("person_email", type=str)

    def handle(self, *args, person_email, **options):
        try:
            p = Person.objects.get_by_natural_key(person_email)
        except Person.DoesNotExist:
            raise CommandError("L'email donné est inconnu.")

        extract = {}
        personal = extract["information personnelle"] = {
            "emails": [e.address for e in p.emails.all()],
            **get_all_fields(p),
        }
        personal["pays"] = str(personal["pays"])  # not serializable

        org_events = extract["événements organisés"] = []
        attended_events = extract["participations aux événements"] = []
        memberships = extract["participations à des groupes"] = []
        payments = extract["paiements"] = []
        event_images = extract["photos postées"] = []
        form_subs = extract["soumissions de formulaires"] = []
        tags = extract["tags"] = []

        for m in p.memberships.select_related("supportgroup"):
            memberships.append(
                {
                    "Nom du groupe": m.supportgroup.name,
                    "URL du groupe": urljoin(
                        settings.FRONT_DOMAIN,
                        reverse("view_group", args=(m.supportgroup_id,)),
                    ),
                    **get_all_fields(m),
                }
            )

        for o in p.organizer_configs.select_related("event"):
            org_events.append(
                {
                    "Nom de l'événement": o.event.name,
                    "URL de l'événement": urljoin(
                        settings.FRONT_DOMAIN, reverse("view_event", args=(o.event,))
                    )
                    ** get_all_fields(o),
                }
            )

        for s in p.rsvps.select_related("event"):
            attended_events.append(
                {
                    "Nom de l'événement": s.event.name,
                    "URL de l'événement": urljoin(
                        settings.FRONT_DOMAIN, reverse("view_event", args=(s.event,))
                    )
                    ** get_all_fields(s),
                }
            )

        for p in p.payments.all():
            payments.append(get_all_fields(p))

        for i in p.event_images.all():
            event_images.append(get_all_fields(i))

        for s in p.form_submissions.all():
            form_subs.append(get_all_fields(s))

        for t in p.tags.all():
            tags.append(get_all_fields(t))

        json.dump(extract, self.stdout, cls=DjangoJSONEncoder)
