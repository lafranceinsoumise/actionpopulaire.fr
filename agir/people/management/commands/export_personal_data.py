import datetime
import json
from json import JSONEncoder
from uuid import UUID

from django.core.management import CommandError
from django.db.models.fields.related import RelatedField
from django_countries.fields import Country

from agir.lib.commands import BaseCommand
from agir.people.models import Person


class ExportJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(
            o,
            (
                datetime.date,
                datetime.datetime,
            ),
        ):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)

        if isinstance(o, Country):
            return o.code

        return super().default(o)


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("email")

    def execute(self, email, dry_run=False, silent=False, **options):
        try:
            person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            raise CommandError("Pas de personne avec cette adresse email.")

        data = person.as_json()
        self.stdout.write(
            json.dumps(data, indent=4, sort_keys=True, cls=ExportJSONEncoder)
        )
        self.stdout.write("\n")
