# Generated by Django 3.1.13 on 2021-07-26 09:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0003_2022_group_type_refactor"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="membership",
            options={
                "ordering": ["-membership_type"],
                "verbose_name": "adhésion",
                "verbose_name_plural": "adhésions",
            },
        ),
        migrations.AlterField(
            model_name="membership",
            name="membership_type",
            field=models.IntegerField(
                choices=[
                    (5, "Abonné⋅e du groupe"),
                    (10, "Membre actif du groupe"),
                    (50, "Membre gestionnaire"),
                    (100, "Animateur⋅rice"),
                ],
                default=5,
                verbose_name="Statut dans le groupe",
            ),
        ),
    ]
