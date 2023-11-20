# Generated by Django 3.2.23 on 2023-11-16 11:52

import agir.lib.form_fields
import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("polls", "0018_poll_unauthorized_message"),
    ]

    operations = [
        migrations.AddField(
            model_name="polloption",
            name="option_group_id",
            field=models.CharField(
                default="choice",
                help_text="Identifiant d'un groupe qui permettra de regrouper plusieurs options ensemble et definir une configuration spécifique",
                max_length=200,
                verbose_name="Identifiant du groupe d'options",
            ),
        ),
        migrations.AlterField(
            model_name="poll",
            name="rules",
            field=models.JSONField(
                default=dict,
                encoder=django.core.serializers.json.DjangoJSONEncoder,
                help_text="Un object JSON décrivant les règles. Actuellement, sont reconnues `success_url`, `verified_user`, `confirmation_email`, `options`, `min_options`, `max_options`, `shuffle` et `option_groups`",
                verbose_name="Les règles du vote",
            ),
        ),
        migrations.AlterField(
            model_name="pollchoice",
            name="selection",
            field=models.JSONField(encoder=agir.lib.form_fields.CustomJSONEncoder),
        ),
        migrations.AlterUniqueTogether(
            name="pollchoice",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="pollchoice",
            constraint=models.UniqueConstraint(
                fields=("person", "poll"), name="unique_person_and_poll"
            ),
        ),
    ]
