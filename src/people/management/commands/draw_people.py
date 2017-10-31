import sys
import argparse
import csv
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count

from people.models import Person


class Command(BaseCommand):
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

    def handle(self, draw_count, outfile, **kwargs):
        # setting order_by 'gender' so that the created field is not included in the groupby clause
        if draw_count % 2 != 0:
            raise CommandError('Number of persons to draw is not even.')

        counts = {
            d['gender']: d['c'] for d in
            Person.objects.filter(draw_participation=True).order_by('gender').values('gender').annotate(c=Count('gender'))
        }

        total_count = sum(counts[g] for g in [Person.GENDER_FEMALE, Person.GENDER_MALE, Person.GENDER_OTHER])
        other_draw_count = round(draw_count * counts[Person.GENDER_OTHER] / total_count / 2) * 2
        gendered_draw_count = (draw_count - other_draw_count) / 2

        if counts[Person.GENDER_MALE] < gendered_draw_count or counts[Person.GENDER_FEMALE] < gendered_draw_count:
            raise CommandError("Not enough volunteers for drawing with parity")

        participants = Person.objects.none()

        # DRAWING HAPPENS HERE
        for g, n in {Person.GENDER_FEMALE: gendered_draw_count, Person.GENDER_MALE: gendered_draw_count, Person.GENDER_OTHER: other_draw_count}.items():
            participants = participants.union(
                Person.objects.filter(draw_participation=True, gender=g).order_by('?')[:n]
            )

        writer = csv.DictWriter(outfile, fieldnames=['numero', 'id', 'email', 'gender'])
        writer.writeheader()

        for numero, p in enumerate(participants):
            # add one so that sequence numbers start with 1
            writer.writerow({'numero': numero+1, 'id': p.id, 'email': p.email, 'gender': p.gender})
