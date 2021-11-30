from django.core.management import BaseCommand

from agir.lib.tests.mixins import (
    load_fake_data,
    update_fake_data,
    create_people,
    create_groups,
    create_events,
    create_person_forms,
    create_activities,
)


class Command(BaseCommand):
    help = 'Fill the database with fake data. All passwords are "incredible password"'

    def add_arguments(self, parser):
        parser.add_argument(
            "-u",
            "--update",
            action="store_true",
            help="Updates fake data instead of creating it",
        )

        parser.add_argument(
            "--seed_people",
            type=int,
            help="Create n person objects",
        )
        parser.add_argument(
            "--seed_person_forms",
            type=int,
            help="Create n person form objects",
        )
        parser.add_argument(
            "--seed_groups",
            type=int,
            help="Create n group objects",
        )
        parser.add_argument(
            "--seed_events",
            type=int,
            help="Create n event objects",
        )
        parser.add_argument(
            "--seed_activities",
            type=int,
            help="Create n activity objects",
        )
        parser.add_argument(
            "--email",
            type=str,
            help="The email of the activity related person",
        )

    def handle(self, *args, **options):
        if options["seed_people"]:
            self.stdout.write(
                "Seeding database with %d Person objects" % options["seed_people"]
            )
            create_people(options["seed_people"])
        elif options["seed_person_forms"]:
            self.stdout.write(
                "Seeding database with %d PersonForm objects"
                % options["seed_person_forms"]
            )
            create_person_forms(options["seed_person_forms"])
        elif options["seed_groups"]:
            self.stdout.write(
                "Seeding database with %d SupportGroup objects" % options["seed_groups"]
            )
            create_groups(options["seed_groups"])
        elif options["seed_events"]:
            self.stdout.write(
                "Seeding database with %d Event objects" % options["seed_events"]
            )
            create_events(options["seed_events"])
        elif options["seed_activities"]:
            self.stdout.write(
                "Seeding database with %d Activity objects" % options["seed_activities"]
            )
            create_activities(options["seed_activities"], options["email"])
        elif options["update"] == True:
            self.stdout.write("Updating database fake data")
            update_fake_data()
        else:
            load_fake_data()

        self.stdout.write("Done!")
