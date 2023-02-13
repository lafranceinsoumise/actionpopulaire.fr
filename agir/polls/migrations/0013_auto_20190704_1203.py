# Generated by Django 2.2.2 on 2019-07-04 10:03

import agir.lib.models
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("polls", "0012_auto_20190114_1551")]

    operations = [
        migrations.AlterModelOptions(name="poll", options={"ordering": ("-start",)}),
        migrations.AddField(
            model_name="poll",
            name="confirmation_note",
            field=agir.lib.models.DescriptionField(
                blank=True,
                help_text="Note montrée à l'utilisateur une fois la participation enregistrée.",
                verbose_name="Note après participation",
            ),
        ),
        migrations.AlterField(
            model_name="poll",
            name="description",
            field=agir.lib.models.DescriptionField(
                help_text="Le texte de description affiché pour tous les insoumis",
                verbose_name="Description de la consultation",
            ),
        ),
    ]
