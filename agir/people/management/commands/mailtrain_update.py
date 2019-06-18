from datetime import datetime
import string
from uuid import UUID

from django.core.management import BaseCommand
from django.utils import timezone

from agir.lib.mailtrain import update_person
from agir.people.models import Person

PADDING = "0000000-0000-0000-0000-000000000000"


class Command(BaseCommand):
    help = "Synchronize all the database with mailtrain"

    def handle(self, *args, **kwargs):
        start = datetime.now()
        i = 0

        min_letter = string.hexdigits[timezone.now().day % 8 * 2]
        max_letter = string.hexdigits[(timezone.now().day + 1) % 8 * 2]

        qs = Person.objects.filter(id__gte=UUID(min_letter + PADDING))
        if max_letter > min_letter:
            qs = qs.filter(id__lt=UUID(max_letter + PADDING))

        try:
            for person in qs.iterator():
                update_person(person)
                if kwargs["verbosity"] > 1:
                    print("Updated %s " % person.email)

                i += 1
        except Exception as e:
            duration = datetime.now() - start
            print(
                f"Updated {i} people over {qs.count()} in {str(duration.seconds)} seconds."
            )

            raise e

        duration = datetime.now() - start

        print(
            f"Updated people from {min_letter} to {max_letter} ({str(i)}) in {str(duration.seconds)} seconds."
        )
