import json

from django.conf import settings
from django.contrib.gis.db.models import GeometryField
from django.core.management.base import BaseCommand, CommandError
from django.core.serializers.json import DjangoJSONEncoder
from django_countries.fields import CountryField
from glom import glom, T, Coalesce, Literal
from phonenumber_field.modelfields import PhoneNumberField
from stdimage.models import StdImageField

from agir.authentication.models import Role
from agir.events.models import EventImage
from agir.lib.utils import front_url
from agir.payments.models import Payment, Subscription
from agir.people.models import Person, PersonFormSubmission, PersonTag


def field_expression(f):
    if isinstance(f, PhoneNumberField):
        return (f.name, Coalesce("as_e164", default=""))
    elif isinstance(f, GeometryField):
        return (f.name, str)
    elif isinstance(f, CountryField):
        return (f.name, str)
    elif isinstance(f, StdImageField):
        return (f.name, lambda u: settings.FRONT_DOMAIN + settings.MEDIA_URL + u.url)
    elif f.name == "password":
        return Literal("(caché)")

    return f.name


def get_all_fields(m):
    return {
        str(f.verbose_name): field_expression(f)
        for f in m._meta.get_fields()
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

        spec_role = get_all_fields(Role)

        spec_event = {
            "Nom": "name",
            "URL": ("id", lambda id: front_url("view_event", args=[id])),
        }
        spec_membership = {
            "Nom": "supportgroup.name",
            "URL": ("supportgroup.id", lambda id: front_url("view_group", args=[id])),
            "Animateur": "is_referent",
            "Gestionnaire": "is_manager",
        }

        spec_payment = get_all_fields(Payment)
        spec_subscription = get_all_fields(Subscription)
        spec_event_images = get_all_fields(EventImage)
        spec_form_submissions = get_all_fields(PersonFormSubmission)
        spec_tags = get_all_fields(PersonTag)

        spec_person = {
            **get_all_fields(Person),
            "pays": ("location_country", str),
            "Rôle": ("role", spec_role),
            "événements organisés": ("organized_events", T.all(), [spec_event]),
            "participations aux événements": (
                "rsvps",
                T.all(),
                [("event", spec_event)],
            ),
            "participations à des groupes": ("memberships", T.all(), [spec_membership]),
            "paiements": ("payments", T.all(), [spec_payment]),
            "souscription au don mensuel": Coalesce(
                ("subscription", spec_subscription), default=None
            ),
            "images d'événements": ("event_images", T.all(), [spec_event_images]),
            "réponses à des formulaires": (
                "form_submissions",
                T.all(),
                [spec_form_submissions],
            ),
            "libellés": ("tags", T.all(), [spec_tags]),
        }

        self.stdout.ending = ""
        json.dump(glom(p, spec_person), self.stdout, cls=DjangoJSONEncoder)
