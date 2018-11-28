import argparse
from random import sample

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from django.db import connection
from django.utils import timezone

from agir.groups.models import SupportGroupSubtype
from agir.people.models import Person, PersonTag


CERTIFIED_QUERY = """
SELECT DISTINCT person."id" FROM "people_person" person
INNER JOIN "groups_membership" membership ON (person.id = membership.person_id)
INNER JOIN "groups_supportgroup" supportgroup ON (membership.supportgroup_id = supportgroup.id)
INNER JOIN "groups_supportgroup_subtypes" subtype ON (supportgroup.id = subtype.supportgroup_id)
WHERE person."draw_participation" = TRUE
AND person."id" NOT IN %(exclude_ids)s
AND person."created" < %(date)s
AND person."gender" = %(gender)s
AND subtype."supportgroupsubtype_id" = %(subtype)s
AND membership."created" < %(date)s;
"""

NOT_CERTIFIED_QUERY = """
SELECT DISTINCT person."id" FROM "people_person" person
WHERE person."draw_participation" = TRUE
AND person."id" NOT IN %(exclude_ids)s
AND person."created" < %(date)s
AND person."gender" = %(gender)s
AND NOT EXISTS (
  SELECT 1 FROM "groups_membership" membership
  INNER JOIN "groups_supportgroup" supportgroup ON (membership.supportgroup_id = supportgroup.id)
  INNER JOIN "groups_supportgroup_subtypes" subtype ON (supportgroup.id = subtype.supportgroup_id)
  WHERE membership."person_id" = person."id"
  AND subtype."supportgroupsubtype_id" = %(subtype)s
  AND membership."created" < %(date)s
);
"""


def request_executor(request, parameters):
    with connection.cursor() as cursor:
        cursor.execute(request, parameters)
        rows = cursor.fetchall()
    for row in rows:
        yield row[0]


class Command(BaseCommand):
    date_format = "%d/%m/%Y"

    help = (
        "Draw people at random amongst people who volunteered for it, while ensuring parity between women/men"
        " and fair representation of people who selected 'Other/Not defined' as gender"
    )
    requires_migrations_checks = True

    def date(self, d):
        try:
            return timezone.get_default_timezone().localize(
                timezone.datetime.strptime(d, self.date_format)
            )
        except ValueError:
            raise argparse.ArgumentTypeError(f"{d} is not a valid date")

    def draw(self, it, draw_count, tag):
        (tag, created) = PersonTag.objects.get_or_create(label=tag)
        for id in sample(list(it), k=int(draw_count)):
            person = Person.objects.get(pk=id)
            person.tags.add(tag)

    def add_arguments(self, parser):
        parser.add_argument("reference_date", type=self.date)
        parser.add_argument("draw_count", type=int)
        parser.add_argument("tag", action="store")

        parser.add_argument("-g", "--gender")

        parser.add_argument(
            "-c", "--certified-on", dest="certified", action="store_true"
        )
        parser.add_argument(
            "-n", "--not-certified-on", dest="not_certified", action="store_true"
        )
        parser.add_argument(
            "-p", "--previous-tags", dest="previous_tags", action="append", default=[]
        )

    def handle(
        self,
        reference_date,
        draw_count,
        tag,
        gender,
        certified,
        not_certified,
        previous_tags,
        **kwargs,
    ):
        exclude_ids = [
            p.id for p in Person.objects.filter(tags__label__in=previous_tags)
        ]

        if certified and not_certified:
            raise CommandError("Set either --certified-only OR --not-certified-only")

        college = (
            "certified" if certified else "not-certified" if not_certified else "all"
        )

        certified_subtype = SupportGroupSubtype.objects.get(label="certifié")

        if not_certified:
            pk_iterator = lambda g: request_executor(
                NOT_CERTIFIED_QUERY,
                {
                    "date": reference_date,
                    "exclude_ids": exclude_ids,
                    "gender": g,
                    "subtype": certified_subtype.id,
                },
            )
        elif certified:
            pk_iterator = lambda g: request_executor(
                CERTIFIED_QUERY,
                {
                    "date": reference_date,
                    "exclude_ids": exclude_ids,
                    "gender": g,
                    "subtype": certified_subtype.id,
                },
            )

        else:
            base_qs = Person.objects.filter(
                draw_participation=True, created__lt=reference_date
            ).exclude(id__in=exclude_ids)
            pk_iterator = (
                lambda g: base_qs.filter(gender=g)
                .values_list("id", flat=True)
                .distinct()
            )

        if not gender:
            # setting order_by 'gender' so that the created field is not included in the groupby clause
            counts = {
                d["gender"]: d["c"]
                for d in base_qs.order_by("gender")
                .values("gender")
                .annotate(c=Count("gender"))
            }

            total_count = sum(
                counts[g]
                for g in [Person.GENDER_FEMALE, Person.GENDER_MALE, Person.GENDER_OTHER]
            )
            other_draw_count = (
                round(draw_count * counts[Person.GENDER_OTHER] / total_count / 2) * 2
            )
            gendered_draw_count = round((draw_count - other_draw_count) / 2)

            if (
                counts[Person.GENDER_MALE] < gendered_draw_count
                or counts[Person.GENDER_FEMALE] < gendered_draw_count
            ):
                raise CommandError("Not enough volunteers for drawing with parity")

            draws = {
                Person.GENDER_FEMALE: gendered_draw_count,
                Person.GENDER_MALE: gendered_draw_count,
                Person.GENDER_OTHER: other_draw_count,
            }

        else:
            draws = {gender: draw_count}

        # DRAWING HAPPENS HERE
        for g, n in draws.items():
            self.draw(pk_iterator(g), n, tag + " " + g)

        print(
            f"Drew {gendered_draw_count} women, {gendered_draw_count} men and {other_draw_count} others."
        )
