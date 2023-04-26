# Generated by Django 3.2.18 on 2023-04-13 09:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0024_personform_meta_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="action_radius",
            field=models.PositiveIntegerField(
                default=100,
                help_text="Le rayon en km utilisé pour suggérer des actions autour de la position géographique de la personne",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(500),
                ],
                verbose_name="Zone d'action (Km)",
            ),
        ),
    ]