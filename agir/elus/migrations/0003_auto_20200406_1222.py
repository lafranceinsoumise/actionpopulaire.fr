# Generated by Django 2.2.12 on 2020-04-06 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("elus", "0002_mandatmunicipal_reseau"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mandatmunicipal",
            name="mandat",
            field=models.CharField(
                blank=True,
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
    ]
