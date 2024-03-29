# Generated by Django 3.1.13 on 2021-07-21 16:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0005_add_subscriptions"),
        ("data_france", "0027_eludepartemental"),
        ("elus", "0025_deputes"),
    ]

    operations = [
        migrations.AddField(
            model_name="mandatdepartemental",
            name="reference",
            field=models.ForeignKey(
                blank=True,
                help_text="La fiche correspondant à cet élu dans le Répertoire National des Élus",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="elus",
                related_query_name="elu",
                to="data_france.eludepartemental",
                verbose_name="Référence dans le RNE",
            ),
        ),
        migrations.AlterField(
            model_name="accesapplicationparrainages",
            name="person",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="acces_application_parrainages",
                to="people.person",
            ),
        ),
        migrations.AlterField(
            model_name="mandatdepute",
            name="reference",
            field=models.ForeignKey(
                blank=True,
                help_text="La fiche correspondant à cet élu dans la base de l'AN",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="elus",
                related_query_name="elu",
                to="data_france.depute",
                verbose_name="Référence dans les données AN",
            ),
        ),
        migrations.AlterField(
            model_name="mandatmunicipal",
            name="reference",
            field=models.ForeignKey(
                blank=True,
                help_text="La fiche correspondant à cet élu dans le Répertoire National des Élus",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="elus",
                related_query_name="elu",
                to="data_france.elumunicipal",
                verbose_name="Référence dans le RNE",
            ),
        ),
    ]
