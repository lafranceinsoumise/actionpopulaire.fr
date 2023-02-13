# Generated by Django 3.2.16 on 2023-02-03 11:12

import agir.lib.form_fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0014_boucles_departementales"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="meta",
            field=models.JSONField(
                blank=True,
                default=dict,
                encoder=agir.lib.form_fields.CustomJSONEncoder,
                verbose_name="Données supplémentaires",
            ),
        ),
    ]
