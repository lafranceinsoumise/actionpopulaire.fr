# Generated by Django 3.1.11 on 2021-06-16 08:52

import agir.lib.model_fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0004_event_online_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="facebook",
            field=agir.lib.model_fields.FacebookEventField(
                blank=True,
                max_length=255,
                verbose_name="Événement correspondant sur Facebook",
            ),
        ),
    ]
