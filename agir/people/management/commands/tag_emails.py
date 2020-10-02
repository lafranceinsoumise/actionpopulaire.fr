import re
import sys

from django.core.management.base import BaseCommand
from tqdm import tqdm

from ...models import Person, PersonTag


class Command(BaseCommand):
    help = "Tag all emails found in standard input"
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
        emails = re.findall(self.EMAIL_RE, sys.stdin.read())

        self.stdout.write(f"{len(emails)} email addresses found...")

        persons = []
        missing = 0

        if tmp is False:
            tag_object, created = PersonTag.objects.get_or_create(label=tag)
            if created:
                self.stdout.write(f"Tag {tag} did not exist. Created... ")

        for e in tqdm(emails):
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

        if create:
            self.stdout.write(f"Users for {missing} / {len(emails)} were created.")
        else:
            self.stdout.write(f"{missing} / {len(emails)} emails were not found")
