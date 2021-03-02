import re
import sys

import phonenumbers
from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Person, PersonTag


class Command(BaseCommand):
    help = "Tag all emails or phone numbers found in standard input"
    EMAIL_RE = r"[a-zA-Z0-9!#$%&'*+/=?^_`{|}~.-]+@[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)+"

    def add_arguments(self, parser):
        parser.add_argument("tag")

        parser.add_argument(
            "-c",
            "--create-missing",
            action="store_true",
            dest="create",
            default=False,
            help=(
                "In case emails without a corresponding account are found in input, create "
                "a corresponding account and add it with the tag. By default those accounts are non"
                "members account. WARNING: make sure you have the full consent of all concerned individuals."
            ),
        )
        parser.add_argument(
            "-i",
            "--insoumis",
            action="store_true",
            dest="insoumis",
            default=False,
            help=("Make new accounts full members."),
        )
        parser.add_argument(
            "--tmp",
            action="store_true",
            dest="tmp",
            default=False,
            help=(
                "Does not write the tag in api. If create missing is off, the command does nothing."
            ),
        )

    def handle(self, *args, tag, create, insoumis, tmp, **options):
        entry = sys.stdin.read()
        emails = re.findall(self.EMAIL_RE, entry)
        numbers = []
        for line in entry.splitlines():
            try:
                numbers.append(phonenumbers.parse(line, "FR"))
            except phonenumbers.NumberParseException:
                pass

        self.stdout.write(
            f"{len(emails)} email addresses and {len(numbers)} numbers found..."
        )

        persons = []
        missing = 0

        if tmp is False:
            tag_object, created = PersonTag.objects.get_or_create(label=tag)
            if created:
                self.stdout.write(f"Tag {tag} did not exist. Created... ")

        with tqdm(total=len(emails) + len(numbers)) as progress:
            for e in emails:
                progress.update(1)
                try:
                    person = Person.objects.get_by_natural_key(e)
                except Person.DoesNotExist:
                    missing += 1
                    if create:
                        person = Person.objects.create_person(
                            email=e, is_insoumise=insoumis
                        )
                    else:
                        continue

                if tmp is False:
                    # noinspection PyUnboundLocalVariable
                    tag_object.people.add(person)

            for n in numbers:
                progress.update(1)
                person = Person.objects.filter(contact_phone=n).first()
                if person is None:
                    missing += 1
                    if create:
                        person = Person.objects.create_person(
                            email=None, contact_phone=n, is_insoumise=insoumis
                        )
                    else:
                        continue

                if tmp is False:
                    # noinspection PyUnboundLocalVariable
                    tag_object.people.add(person)

        if create:
            self.stdout.write(f"{missing} users were created.")
        else:
            self.stdout.write(f"{missing} users were not found")
