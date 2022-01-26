# Generated by Django 3.1.12 on 2021-06-23 13:53

import agir.gestion.models.common
from django.db import migrations, models

import agir.lib.utils


class Migration(migrations.Migration):

    dependencies = [
        ("gestion", "0003_auto_20210623_1525"),
    ]

    operations = [
        migrations.AddField(
            model_name="instancecherchable",
            name="numero",
            field=models.CharField(
                blank=True,
                default=agir.lib.utils.numero_unique,
                editable=False,
                help_text="Numéro unique pour identifier chaque objet sur la plateforme.",
                max_length=7,
                unique=True,
                verbose_name="Numéro unique",
            ),
        ),
    ]
