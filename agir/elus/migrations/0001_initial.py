# Generated by Django 2.2.11 on 2020-03-31 14:52

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("people", "0001_creer_modeles"),
        ("data_france", "0005_auto_20200330_0827"),
    ]

    operations = [
        migrations.CreateModel(
            name="MandatMunicipal",
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
                        default=datetime.date(2020, 3, 22),
                        verbose_name="Date de début du mandat",
                    ),
                ),
                (
                    "fin",
                    models.DateField(
                        default=datetime.date(2026, 3, 1),
                        help_text="Date légale si dans le future, date effective si dans le passé.",
                        verbose_name="Date de fin du mandat",
                    ),
                ),
                (
                    "mandat",
                    models.CharField(
                        choices=[
                            ("MAJ", "Conseiller⋅e municipal de la majorité"),
                            ("OPP", "Conseiller⋅e municipal de l'opposition"),
                            ("MAI", "Maire"),
                            ("ADJ", "Adjoint⋅e au maire"),
                            ("MDA", "Maire d'une commune déléguée ou associée"),
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
                    "communautaire",
                    models.BooleanField(
                        default=False, verbose_name="Élu dans l'intercommunalité"
                    ),
                ),
                (
                    "commune",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="data_france.Commune",
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
                        on_delete=django.db.models.deletion.CASCADE, to="people.Person"
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Mandats municipaux",
            },
        ),
    ]
