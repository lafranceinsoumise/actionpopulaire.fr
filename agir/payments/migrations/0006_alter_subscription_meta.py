# Generated by Django 3.2.23 on 2024-01-26 16:15

import agir.lib.form_fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0005_subscription_effect_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="meta",
            field=models.JSONField(
                blank=True, default=dict, encoder=agir.lib.form_fields.CustomJSONEncoder
            ),
        ),
    ]
