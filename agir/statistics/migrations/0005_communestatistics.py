# Generated by Django 3.2.20 on 2023-10-27 14:42

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("data_france", "0037_alter_deputeeuropeen_options"),
        ("statistics", "0004_absolutestatistics_liaison_count"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommuneStatistics",
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
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                (
                    "date",
                    models.DateField(
                        db_index=True, editable=False, unique=False, verbose_name="Date"
                    ),
                ),
                (
                    "population",
                    models.IntegerField(default=0, verbose_name="Population"),
                ),
                (
                    "local_supportgroup_count",
                    models.IntegerField(
                        default=0, verbose_name="Groupes d'actions locaux"
                    ),
                ),
                (
                    "local_certified_supportgroup_count",
                    models.IntegerField(
                        default=0, verbose_name="Groupes d'actions locaux certifiés"
                    ),
                ),
                (
                    "event_count",
                    models.IntegerField(default=0, verbose_name="Événements"),
                ),
                (
                    "people_count",
                    models.IntegerField(default=0, verbose_name="Personnes"),
                ),
                (
                    "commune",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="statistics",
                        related_query_name="statistics",
                        to="data_france.commune",
                        verbose_name="commune",
                    ),
                ),
            ],
            options={
                "verbose_name": "statistique par commune",
                "verbose_name_plural": "statistiques par commune",
                "ordering": ("-date",),
                "get_latest_by": "date",
            },
        ),
        migrations.AddIndex(
            model_name="communestatistics",
            index=models.Index(
                fields=["population"], name="statistics__populat_bd787f_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="communestatistics",
            constraint=models.UniqueConstraint(
                fields=("date", "commune"), name="unique_for_date_and_commune"
            ),
        ),
    ]
