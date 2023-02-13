import agir.elus.models
import datetime
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("elus", "0005_auto_20200410_1617"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mandatmunicipal",
            options={
                "ordering": ("conseil", "person"),
                "verbose_name_plural": "Mandats municipaux",
            },
        ),
        migrations.RenameField(
            model_name="mandatmunicipal",
            old_name="commune",
            new_name="conseil",
        ),
        migrations.RenameField(
            model_name="mandatmunicipal", old_name="reseau", new_name="statut"
        ),
        migrations.AlterField(
            model_name="mandatmunicipal",
            name="conseil",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="data_france.Commune",
                verbose_name="Commune",
            ),
        ),
        migrations.AlterField(
            model_name="mandatmunicipal",
            name="statut",
            field=models.CharField(
                choices=[
                    ("INC", "Mandat à vérifier (ajouté côté admin)"),
                    ("DEM", "Mandat à vérifier (ajouté par la personne elle-même)"),
                    ("INS", "Mandat vérifié"),
                ],
                default="INC",
                max_length=3,
                verbose_name="Statut",
            ),
        ),
        migrations.AlterField(
            model_name="mandatmunicipal",
            name="fin",
            field=models.DateField(
                default=datetime.date(2026, 3, 1),
                help_text="Date légale si dans le futur, date effective si dans le passé.",
                verbose_name="Date de fin du mandat",
            ),
        ),
        migrations.CreateModel(
            name="MandatRegional",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "debut",
                    models.DateField(
                        default=datetime.date(2015, 12, 13),
                        verbose_name="Date de début du mandat",
                    ),
                ),
                (
                    "fin",
                    models.DateField(
                        default=datetime.date(2021, 3, 31),
                        help_text="Date légale si dans le futur, date effective si dans le passé.",
                        verbose_name="Date de fin du mandat",
                    ),
                ),
                (
                    "mandat",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("MAJ", "Conseiller⋅e majoritaire"),
                            ("OPP", "Conseiller⋅e minoritaire"),
                            ("PRE", "Président du conseil"),
                            ("VPR", "Vice-Président"),
                        ],
                        max_length=3,
                        verbose_name="Type de mandat",
                    ),
                ),
                (
                    "delegations_municipales",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("social", "Action sociale"),
                                (
                                    "civiles juridiques",
                                    "Affaires civiles et juridiques",
                                ),
                                ("économie", "Affaires économiques"),
                                ("école", "Affaires scolaires"),
                                ("agriculture", "Agriculture"),
                                ("veterans", "Anciens combattants"),
                                ("cantines", "Cantines"),
                                ("commerce", "Commerce"),
                                ("cimetières", "Cimetières"),
                                ("international", "Coopération internationale"),
                                ("culture", "Culture"),
                                ("eau", "Eau assainissement"),
                                ("égalité F/H", "Égalité F/H"),
                                ("emploi", "Emploi"),
                                ("environnement", "Environnement"),
                                ("finances", "Finances"),
                                ("handicap", "Handicap"),
                                ("jeunesse", "Jeunesse"),
                                ("logement", "Logement"),
                                ("personnel", "Personnel"),
                                ("discriminations", "Luttes contre discriminations"),
                                ("personnes agées", "Personnes âgées"),
                                ("petite enfance", "Petite enfance"),
                                ("propreté", "Propreté"),
                                ("santé", "Santé"),
                                ("sécurité", "Sécurité"),
                                ("sport", "Sport"),
                                ("tourisme", "Tourisme"),
                                ("déchets", "Traitement des déchets"),
                                ("transport", "Transport"),
                                ("travaux", "Travaux"),
                                ("urbanisme", "Urbanisme"),
                                ("associations", "Vie associative"),
                                ("voirie", "Voirie"),
                            ],
                            max_length=20,
                        ),
                        blank=True,
                        default=list,
                        size=None,
                        verbose_name="Délégations",
                    ),
                ),
                (
                    "statut",
                    models.CharField(
                        choices=[
                            ("INC", "Mandat à vérifier (ajouté côté admin)"),
                            (
                                "DEM",
                                "Mandat à vérifier (ajouté par la personne elle-même)",
                            ),
                            ("INS", "Mandat vérifié"),
                        ],
                        default="INC",
                        max_length=3,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "conseil",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_france.CollectiviteRegionale",
                        verbose_name="Conseil régional (ou de collectivité unique)",
                    ),
                ),
                (
                    "email_officiel",
                    models.ForeignKey(
                        help_text="L'adresse avec laquelle contacter l'élu pour des questions officielles",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="people.PersonEmail",
                        verbose_name="Adresse email officielle",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="people.Person",
                        verbose_name="Élu",
                    ),
                ),
            ],
            options={
                "verbose_name": "Mandat régional",
                "verbose_name_plural": "Mandats régionaux",
                "ordering": ("conseil", "person"),
                "unique_together": {("conseil", "person")},
            },
            bases=(agir.elus.models.mandats.MandatHistoryMixin, models.Model),
        ),
        migrations.CreateModel(
            name="MandatDepartemental",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "debut",
                    models.DateField(
                        default=datetime.date(2015, 3, 29),
                        verbose_name="Date de début du mandat",
                    ),
                ),
                (
                    "fin",
                    models.DateField(
                        default=datetime.date(2021, 3, 31),
                        help_text="Date légale si dans le futur, date effective si dans le passé.",
                        verbose_name="Date de fin du mandat",
                    ),
                ),
                (
                    "mandat",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("MAJ", "Conseiller⋅e majoritaire"),
                            ("OPP", "Conseiller⋅e minoritaire"),
                            ("PRE", "Président du conseil"),
                            ("VPR", "Vice-Président"),
                        ],
                        max_length=3,
                        verbose_name="Type de mandat",
                    ),
                ),
                (
                    "delegations_municipales",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("social", "Action sociale"),
                                (
                                    "civiles juridiques",
                                    "Affaires civiles et juridiques",
                                ),
                                ("économie", "Affaires économiques"),
                                ("école", "Affaires scolaires"),
                                ("agriculture", "Agriculture"),
                                ("veterans", "Anciens combattants"),
                                ("cantines", "Cantines"),
                                ("commerce", "Commerce"),
                                ("cimetières", "Cimetières"),
                                ("international", "Coopération internationale"),
                                ("culture", "Culture"),
                                ("eau", "Eau assainissement"),
                                ("égalité F/H", "Égalité F/H"),
                                ("emploi", "Emploi"),
                                ("environnement", "Environnement"),
                                ("finances", "Finances"),
                                ("handicap", "Handicap"),
                                ("jeunesse", "Jeunesse"),
                                ("logement", "Logement"),
                                ("personnel", "Personnel"),
                                ("discriminations", "Luttes contre discriminations"),
                                ("personnes agées", "Personnes âgées"),
                                ("petite enfance", "Petite enfance"),
                                ("propreté", "Propreté"),
                                ("santé", "Santé"),
                                ("sécurité", "Sécurité"),
                                ("sport", "Sport"),
                                ("tourisme", "Tourisme"),
                                ("déchets", "Traitement des déchets"),
                                ("transport", "Transport"),
                                ("travaux", "Travaux"),
                                ("urbanisme", "Urbanisme"),
                                ("associations", "Vie associative"),
                                ("voirie", "Voirie"),
                            ],
                            max_length=20,
                        ),
                        blank=True,
                        default=list,
                        size=None,
                        verbose_name="Délégations",
                    ),
                ),
                (
                    "statut",
                    models.CharField(
                        choices=[
                            ("INC", "Mandat à vérifier (ajouté côté admin)"),
                            (
                                "DEM",
                                "Mandat à vérifier (ajouté par la personne elle-même)",
                            ),
                            ("INS", "Mandat vérifié"),
                        ],
                        default="INC",
                        max_length=3,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "conseil",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_france.CollectiviteDepartementale",
                        verbose_name="Conseil départemental (ou de métropole)",
                    ),
                ),
                (
                    "email_officiel",
                    models.ForeignKey(
                        help_text="L'adresse avec laquelle contacter l'élu pour des questions officielles",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="people.PersonEmail",
                        verbose_name="Adresse email officielle",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="people.Person",
                        verbose_name="Élu",
                    ),
                ),
            ],
            options={
                "verbose_name": "Mandat départemental",
                "verbose_name_plural": "Mandats départementaux",
                "ordering": ("conseil", "person"),
                "unique_together": {("conseil", "person")},
            },
            bases=(agir.elus.models.mandats.MandatHistoryMixin, models.Model),
        ),
    ]
