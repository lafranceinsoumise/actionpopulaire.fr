from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count
from random import sample

from agir.lib.management_utils import date_as_local_datetime_argument, event_argument
from agir.people.models import Person, PersonTag


class Command(BaseCommand):
    help = (
        "Draw people at random amongst people who volunteered for it, while ensuring parity between women/men"
        " and fair representation of people who selected 'Other/Not defined' as gender"
    )
    requires_migrations_checks = True

    def draw(self, it, draw_count, tag):
        tag = PersonTag.objects.create(label=tag)
        for id in sample(list(it), k=int(draw_count)):
            person = Person.objects.get(pk=id)
            person.tags.add(tag)

    def add_arguments(self, parser):
        parser.add_argument("reference_date", type=date_as_local_datetime_argument)
        parser.add_argument("target", type=int)
        parser.add_argument("tag_prefix", action="store")
        parser.add_argument("event", type=event_argument)

    def display_gendered_information(self, d):
        self.stdout.write(
            f"Femmes :\t{d[Person.GENDER_FEMALE]}\n"
            f"Hommes :\t{d[Person.GENDER_MALE]}\n"
            f"Autres :\t{d[Person.GENDER_OTHER]}\n"
        )

    # noinspection PyUnboundLocalVariable
    def handle(self, reference_date, target, tag_prefix, event, **kwargs):
        previous_tags = PersonTag.objects.filter(label__startswith=tag_prefix)

        new_index = (
            max((int(t.label.split(" ")[-2]) for t in previous_tags), default=0) + 1
        )

        already_drawn_counts = Counter()
        already_rsvped_counts = Counter()

        for tag in previous_tags:
            already_drawn_counts[tag.label[-1]] += tag.people.count()
            if event:
                already_rsvped_counts[tag.label[-1]] += (
                    tag.people.filter(rsvps__event=event)
                    .order_by("id")
                    .distinct("id")
                    .count()
                )

        self.stdout.write("Tirés")
        self.display_gendered_information(already_drawn_counts)
        self.stdout.write("Inscrits")
        self.display_gendered_information(already_rsvped_counts)

        base_qs = (
            Person.objects.filter(
                draw_participation=True,
                created__lt=reference_date,
                newsletters__contains=[Person.NEWSLETTER_LFI],
            )
            .exclude(tags__in=previous_tags)
            .exclude(gender="")
        )
        pk_iterator = (
            lambda g: base_qs.filter(gender=g)
            .order_by("id")
            .distinct("id")
            .values_list("id", flat=True)
        )

        # setting order_by 'gender' so that the created field is not included in the groupby clause
        total_counts = {
            d["gender"]: d["c"]
            for d in base_qs.order_by("gender")
            .values("gender")
            .annotate(c=Count("gender"))
        }

        total_count = sum(total_counts.values())
        target_other_participants = (
            round(target * total_counts[Person.GENDER_OTHER] / total_count / 2) * 2
        )
        target_gendered_participants = round((target - target_other_participants) / 2)

        targets = {
            Person.GENDER_MALE: target_gendered_participants,
            Person.GENDER_FEMALE: target_gendered_participants,
            Person.GENDER_OTHER: target_other_participants,
        }

        if event:
            suggested_draws = self.number_drawns(
                already_drawn_counts, already_rsvped_counts, targets
            )
        else:
            suggested_draws = targets

        adjustment = 1.0
        while adjustment:
            draws = {g: int(n * adjustment) for g, n in suggested_draws.items()}

            self.stdout.write("Tirage")
            self.display_gendered_information(draws)

            adjustment = float(
                input("Indiquez le taux d'ajustement (par défaut 1) : ") or 0
            )

        if (
            total_counts[Person.GENDER_MALE] < draws[Person.GENDER_MALE]
            or total_counts[Person.GENDER_FEMALE] < draws[Person.GENDER_FEMALE]
        ):
            raise CommandError("Pas assez de volontaires pour tirer")

        # DRAWING HAPPENS HERE
        for g, n in draws.items():
            self.draw(pk_iterator(g), n, f"{tag_prefix} {new_index} {g}")

        self.stdout.write("Tiré au sort")
        self.display_gendered_information(draws)

    def number_drawns(self, already_drawn_counts, already_rsvped_counts, targets):
        rates = {
            g: max(already_rsvped_counts[g] / already_drawn_counts[g], 0.05)
            for g in already_drawn_counts
        }
        self.stdout.write("Taux de réponse jusqu'à maintenant")
        self.display_gendered_information(rates)

        real_targets = {g: targets[g] - already_rsvped_counts[g] for g in targets}

        return {g: real_targets[g] / rates[g] for g in real_targets}
