from datetime import datetime
import string
from django.core.management import BaseCommand
from django.utils import timezone

from agir.lib.mailtrain import update_person
from agir.people.models import Person


class Command(BaseCommand):
    help = "Synchronize all the database with mailtrain"

    def handle(self, *args, **kwargs):
        start = datetime.now()
        i = 0

        min_letter = string.hexdigits[timezone.now().day % 8 * 2]
        max_letter = string.hexdigits[(timezone.now().day + 1) % 8 * 2]

        for person in Person.objects.filter(
            id__gt=min_letter, id__lt=max_letter
        ).iterator():
            update_person(person)
            if kwargs["verbosity"] > 1:
                print("Updated %s " % person.email)

            i += 1

        duration = datetime.now() - start

        print(
            f"Updated people from {min_letter} to {max_letter} ({str(i)}) in {str(duration.seconds)} seconds."
        )
