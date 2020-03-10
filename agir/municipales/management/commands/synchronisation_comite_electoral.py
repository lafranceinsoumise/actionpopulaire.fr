from collections import defaultdict
from itertools import groupby
from uuid import UUID

import pandas as pd
from django.core.management import BaseCommand
from operator import itemgetter

from agir.municipales.models import CommunePage
from agir.people.models import PersonTag, Person, PersonForm


class Command(BaseCommand):
    help = "Met à jour les listes que l'on soutient"

    def add_arguments(self, parser):
        parser.add_argument("source")

    def handle(self, *args, source, **options):
        df = self.get_reference_file(source)

        all_communes = {
            c.code: c for c in CommunePage.objects.filter(code__in=df.index)
        }

        unknown_person, unknown_insee = self.tag_chefs_file(df, all_communes)

        if unknown_insee:
            self.stderr.write(f"Codes insee inconnus: {unknown_insee!r}")
        if unknown_person:
            self.stderr.write(f"Emails inconnus: {unknown_person!r}")

        self.publish_pages(df, all_communes)
        self.tag_other_referents()

    @staticmethod
    def get_reference_file(source):
        df = pd.read_csv(source)

        df["Département"] = df["Département"].fillna(method="ffill")
        df = df[df["Code Insee"].notnull()]
        df["Afficher la stratégie"] = (
            df["Afficher la stratégie"].str.strip().str.lower() == "oui"
        ).fillna(False)
        df["Afficher le binôme"] = (
            df["Afficher le binôme"].str.strip().str.lower() == "oui"
        ).fillna(False)

        return df.set_index(df["Code Insee"])

    def tag_chefs_file(self, df, all_communes):
        # liste des tuples (code_insee, email) pour tous les chefs de file
        all_emails = sorted(
            (
                e
                for c in ["Mail Cheffe de file", "Mail Chef de file"]
                for e in df[c].dropna().iteritems()
            ),
            key=itemgetter(0),
        )

        # liste des groupes (communepage_object, [emails])
        grouped = [
            (all_communes[citycode], [email for _, email in elems])
            for citycode, elems in groupby(all_emails, key=itemgetter(0))
            if citycode in all_communes
        ]

        all_ids = []
        unknown_person = defaultdict(list)

        for commune, emails in grouped:
            persons = []

            for e in emails:
                try:
                    p = Person.objects.get_by_natural_key(e)
                except Person.DoesNotExist:
                    unknown_person[commune.code].append(e)
                    continue

                persons.append(p)

            commune.municipales2020_admins.add(*persons)
            commune.municipales2020_admins.remove(
                *commune.municipales2020_admins.exclude(pk__in=[p.pk for p in persons])
            )
            all_ids.extend(p.id for p in persons)

        for p in Person.objects.exclude(id__in=all_ids).filter(
            municipales2020_commune__isnull=False
        ):
            p.municipales2020_commune.remove(*p.municipales2020_commune.all())

        t, created = PersonTag.objects.get_or_create(
            label="Chefs de file municipales 2020"
        )

        t.people.add(*all_ids)
        t.people.remove(*t.people.exclude(pk__in=all_ids))

        unknown_insee = set(df.index).difference(all_communes)
        return unknown_person, unknown_insee

    def publish_pages(self, df, all_communes):
        strategies = pd.DataFrame({"strategie": df["Stratégie adoptée"]})

        strategies["strategie"] = strategies["strategie"].where(
            df["Afficher la stratégie"], ""
        )

        noms = df["Binôme FI"].str.strip().str.split(" - ")
        strategies[["first_name_1", "last_name_1"]] = (
            noms.str.get(0)
            .str.split(" ", 1, expand=True)
            .where(df["Afficher le binôme"])
            .fillna("")
        )
        strategies[["first_name_2", "last_name_2"]] = (
            noms.str.get(1)
            .str.split(" ", 1, expand=True)
            .where(df["Afficher le binôme"])
            .fillna("")
        )

        strategies["tete_liste"] = df["Tête de liste"].fillna("")
        strategies["published"] = df["Afficher la stratégie"] | df["Afficher le binôme"]

        for infos in strategies.itertuples():
            commune = all_communes.get(infos.Index)
            if commune:
                commune.strategy = infos.strategie
                commune.first_name_1 = infos.first_name_1
                commune.last_name_1 = infos.last_name_1
                commune.first_name_2 = infos.first_name_2
                commune.last_name_2 = infos.last_name_2
                commune.tete_liste = infos.tete_liste
                commune.published = infos.published

                commune.save(
                    update_fields=[
                        "strategy",
                        "first_name_1",
                        "last_name_1",
                        "first_name_2",
                        "last_name_2",
                        "tete_liste",
                        "published",
                    ]
                )

    def tag_other_referents(self):
        form = PersonForm.objects.get(slug="chefs-de-file-municipales-2020")
        submissions = (
            form.submissions.filter(
                person__tags__label="Chefs de file municipales 2020"
            )
            .order_by("person_id", "-created")
            .distinct("person_id")
        )

        tags_fields_corr = [
            ("Mandataire financier municipales 2020", "mandataire-mail"),
            ("Référent RS municipales 2020", "rs-mail"),
            ("Référent presse municipales 2020", "presse"),
        ]

        tags = [
            PersonTag.objects.get_or_create(label=t)[0] for t, _ in tags_fields_corr
        ]

        people_ids = [
            {UUID(s.data[field]) for s in submissions if s.data[field]}
            for _, field in tags_fields_corr
        ]

        for tag, ids in zip(tags, people_ids):
            current = set(tag.people.all().values_list("id", flat=True))
            to_add = ids.difference(current)
            to_remove = current.difference(ids)
            tag.people.add(*to_add)
            tag.people.remove(*to_remove)
