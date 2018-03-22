import sys
import argparse
import csv
from itertools import chain
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.utils import timezone

from groups.models import SupportGroupSubtype
from people.models import Person


class Command(BaseCommand):
    date_format = "%d/%m/%Y"

    help = "Draw people at random amongst people who volunteered for it, while ensuring parity between women/men" \
           " and fair representation of people who selected 'Other/Not defined' as gender"
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output',
            dest='outfile', type=argparse.FileType('w'), default=sys.stdout,
            help='Csv file to which the list will be exported'
        )

        parser.add_argument(
            'draw_count',
            type=int
        )

        parser.add_argument('-c', '--certified-on', dest='certified')
        parser.add_argument('-n', '--not-certified-on', dest='not_certified')
        parser.add_argument('-p', '-previous-draw', dest='previous')

    def handle(self, draw_count, outfile, certified, not_certified, previous, **kwargs):
        # setting order_by 'gender' so that the created field is not included in the groupby clause
        if draw_count % 2 != 0:
            raise CommandError('Number of persons to draw is not even.')

        if certified and not_certified:
            raise CommandError('Set either --certified-only OR --not-certified-only')

        base_qs = Person.objects.filter(draw_participation=True)

        certified_subtype = SupportGroupSubtype.objects.get(label="certifié")

        if certified:
            date = timezone.datetime.strptime(certified, self.date_format).replace(tzinfo=timezone.get_default_timezone())
            base_qs = base_qs.filter(memberships__supportgroup__subtypes=certified_subtype, memberships__created__lt=date)
        if not_certified:
            date = timezone.datetime.strptime(not_certified, self.date_format).replace(tzinfo=timezone.get_default_timezone())
            base_qs = base_qs.exclude(memberships__supportgroup__subtypes=certified_subtype, memberships__created__lt=date)

        counts = {
            d['gender']: d['c'] for d in
            base_qs.order_by('gender').values('gender').annotate(c=Count('gender'))
        }

        total_count = sum(counts[g] for g in [Person.GENDER_FEMALE, Person.GENDER_MALE, Person.GENDER_OTHER])
        other_draw_count = round(draw_count * counts[Person.GENDER_OTHER] / total_count / 2) * 2
        gendered_draw_count = (draw_count - other_draw_count) / 2

        if counts[Person.GENDER_MALE] < gendered_draw_count or counts[Person.GENDER_FEMALE] < gendered_draw_count:
            raise CommandError("Not enough volunteers for drawing with parity")

        participants = []

        # DRAWING HAPPENS HERE
        for g, n in {Person.GENDER_FEMALE: gendered_draw_count, Person.GENDER_MALE: gendered_draw_count, Person.GENDER_OTHER: other_draw_count}.items():
            participants.append(base_qs.filter(gender=g).order_by('?')[:n])

        writer = csv.DictWriter(outfile, fieldnames=['numero', 'id', 'email', 'gender'])
        writer.writeheader()

        for numero, p in enumerate(chain.from_iterable(participants)):
            # add one so that sequence numbers start with 1
            writer.writerow({'numero': numero+1, 'id': p.id, 'email': p.email, 'gender': p.gender})
