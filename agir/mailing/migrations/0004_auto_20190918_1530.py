# Generated by Django 2.2.4 on 2019-09-18 13:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("mailing", "0003_segment_events")]

    operations = [
        migrations.AlterField(
            model_name="segment",
            name="last_login",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Limiter aux membres s'étant connecté⋅e pour la dernière fois après cette date",
            ),
        ),
        migrations.AlterField(
            model_name="segment",
            name="registration_date",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Limiter aux membres inscrit⋅e⋅s après cette date",
            ),
        ),
        migrations.AlterField(
            model_name="segment",
            name="supportgroup_status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("m", "Membres de GA"),
                    ("M", "Animateur·ices et gestionnaires de GA"),
                    ("R", "Animateur·ices de GA"),
                ],
                max_length=1,
                verbose_name="Limiter aux membres de groupes ayant ce statut",
            ),
        ),
        migrations.AlterField(
            model_name="segment",
            name="supportgroup_subtypes",
            field=models.ManyToManyField(
                blank=True,
                to="groups.SupportGroupSubtype",
                verbose_name="Limiter aux membres de groupes d'un de ces sous-types",
            ),
        ),
    ]
