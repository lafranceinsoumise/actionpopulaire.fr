import sys
import re

from django.core.management.base import BaseCommand

from ...models import Person, PersonTag


class Command(BaseCommand):
    help = 'Tag all emails found in standard input'
    EMAIL_RE = "[a-zA-Z0-9_.+-]+@[a-zA-Z_-]+(?:\.[a-zA-Z_-]+)+"

    def add_arguments(self, parser):
        parser.add_argument('tag')

        parser.add_argument(
            '-c', '--create-missing',
            action='store_true', dest='create', default=False,
            help=(
                'In case emails without a corresponding account are found in input, create '
                'a corresponding account and add it with the tag. WARNING: make sure you have the '
                'full consent of all concerned individuals.'
            ),
        )

    def handle(self, *args, tag, create, **options):
        emails = re.findall(self.EMAIL_RE, sys.stdin.read())

        persons = []

        for e in emails:
            try:
                persons.append(Person.objects.get_by_natural_key(e))
            except Person.DoesNotExist:
                if create:
                    persons.append(Person.objects.create_person(email=e))
                    self.stdout.write('Created person "{}"'.format(e))
                else:
                    self.stdout.write('Missing person "{}"'.format(e))

        if persons:
            tag_object, created = PersonTag.objects.get_or_create(
                label=tag,
            )

            if created:
                self.stdout.write('Created tag "{}"'.format(tag))

            tag_object.people.add(*persons)
