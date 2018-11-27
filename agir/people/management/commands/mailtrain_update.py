from datetime import datetime
from django.core.management import BaseCommand

from agir.lib.mailtrain import update_person
from agir.people.models import Person


class Command(BaseCommand):
    help = "Synchronize all the database with mailtrain"

    def handle(self, *args, **kwargs):
        start = datetime.now()
        i = 0

        for person in Person.objects.all().iterator():
            update_person(person)
            if kwargs["verbosity"] > 1:
                print("Updated %s " % person.email)

            i += 1

        duration = datetime.now() - start

        print("Updated %d persons in %d seconds." % (i, duration.seconds))
