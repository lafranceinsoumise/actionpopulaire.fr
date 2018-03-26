import sys
import argparse
import csv
from itertools import chain

from sympy import symbols
from sympy.polys import Poly, rem

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from django.utils import timezone

from groups.models import SupportGroupSubtype
from people.models import Person


X = symbols('x')

CORR_CHARS = {i: str(i) for i in range(10)}
CORR_CHARS[10] = 'A'
CORR_CHARS[11] = 'B'
CORR_CHARS[12] = 'C'

INVERSE_CORR = {v:k for k, v in CORR_CHARS.items()}


def normalize_poly(p):
    return Poly.from_list((c % 13 for c in p.all_coeffs()), X)


G = normalize_poly(Poly((X-2)*(X-4)*(X-8)))


def create_code_from_int(c, length=6):
    coeffs = []

    while c:
        coeffs.append(c % 10)
        c = c // 10

    coeffs = list(reversed(coeffs))

    a = Poly.from_list(coeffs, X)
    b = rem(a * X**3, G)

    m = normalize_poly(a * X**3 - b)

    return ''.join(CORR_CHARS[i] for i in m.all_coeffs()).zfill(length)


def decode(c):
    p = Poly.from_list(map(INVERSE_CORR.get, c), X)
    if all(p.subs(X, f) % 13 == 0 for f in [2, 4, 8]):
        return int(c[:-3])
    else:
        return None


class Command(BaseCommand):
    date_format = "%d/%m/%Y"

    help = "Draw people at random amongst people who volunteered for it, while ensuring parity between women/men" \
           " and fair representation of people who selected 'Other/Not defined' as gender"
    requires_migrations_checks = True

    def date(self, d):
        try:
            return timezone.datetime.strptime(d, self.date_format).replace(tzinfo=timezone.get_default_timezone())
        except ValueError:
            raise argparse.ArgumentTypeError(f'{d} is not a valid date')

    def add_arguments(self, parser):
        parser.add_argument(
            '-o', '--output',
            dest='outfile', type=argparse.FileType('w'), default=sys.stdout,
            help='Csv file to which the list will be exported'
        )

        parser.add_argument('reference_date')

        parser.add_argument(
            'draw_count',
            type=self.date
        )

        parser.add_argument('-g', '--gender')

        parser.add_argument('-c', '--certified-on', dest='certified', action='store_true')
        parser.add_argument('-n', '--not-certified-on', dest='not_certified', action='store_true')
        parser.add_argument('-p', '--previous-draw', dest='previous_draws', type=argparse.FileType('r'), action='append')

    def handle(self, draw_count, reference_date, outfile, certified, not_certified, previous_draws, gender, **kwargs):
        ignore_ids = set()
        starting_number = 1

        for p in previous_draws:
            r = csv.DictReader(p)
            previously_drawn = list(r)

            starting_number = max(starting_number, max(decode(p['numero']) for p in previously_drawn) + 1)
            ignore_ids.update(p['id'] for p in previously_drawn)

        if certified and not_certified:
            raise CommandError('Set either --certified-only OR --not-certified-only')

        base_qs = Person.objects.filter(draw_participation=True, created__gt=reference_date).exclude(id__in=ignore_ids)

        certified_subtype = SupportGroupSubtype.objects.get(label="certifié")
        certified_cond = Q(
            memberships__supportgroup__subtypes=certified_subtype,
            memberships__created__lt=reference_date
        )

        if certified:
            base_qs = base_qs.filter(certified_cond)
        if not_certified:
            base_qs = base_qs.exclude(certified_cond)

        if not gender:
            # setting order_by 'gender' so that the created field is not included in the groupby clause
            counts = {
                d['gender']: d['c'] for d in
                base_qs.order_by('gender').values('gender').annotate(c=Count('gender'))
            }

            total_count = sum(counts[g] for g in [Person.GENDER_FEMALE, Person.GENDER_MALE, Person.GENDER_OTHER])
            other_draw_count = round(draw_count * counts[Person.GENDER_OTHER] / total_count / 2) * 2
            gendered_draw_count = (draw_count - other_draw_count) / 2

            if counts[Person.GENDER_MALE] < gendered_draw_count or counts[Person.GENDER_FEMALE] < gendered_draw_count:
                raise CommandError("Not enough volunteers for drawing with parity")

            draws = {
                Person.GENDER_FEMALE: gendered_draw_count,
                Person.GENDER_MALE: gendered_draw_count,
                Person.GENDER_OTHER: other_draw_count
            }

        else:
            draws = {gender: draw_count}

        participants = []

        # DRAWING HAPPENS HERE
        for g, n in draws.items():
            participants.append(base_qs.filter(gender=g).order_by('?')[:n])

        writer = csv.DictWriter(outfile, fieldnames=['numero', 'id', 'email', 'gender'])
        writer.writeheader()

        for numero, p in enumerate(chain.from_iterable(participants)):
            # add one so that sequence numbers start with 1
            writer.writerow({
                'numero': create_code_from_int(numero+starting_number),
                'id': p.id,
                'email': p.email,
                'gender': p.gender
            })
