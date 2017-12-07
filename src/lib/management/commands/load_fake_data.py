from django.core.management import BaseCommand

from lib.tests.mixins import load_fake_data


class Command(BaseCommand):
    help='Fill the database with fake data. All passwords are "incredible password"'

    def handle(self, *args, **options):
        load_fake_data()