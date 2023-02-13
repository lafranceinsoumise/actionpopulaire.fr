# Generated by Django 3.1.5 on 2021-01-20 21:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("data_france", "0015_recherche_elus_municipaux"),
        ("elus", "0015_auto_20201116_1858"),
    ]

    operations = [
        migrations.AddField(
            model_name="mandatmunicipal",
            name="reference",
            field=models.OneToOneField(
                blank=True,
                help_text="La fiche correspondant à cet élu dans le Répertoire National des Élus",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="data_france.elumunicipal",
                verbose_name="Référence dans le RNE",
            ),
        ),
    ]
