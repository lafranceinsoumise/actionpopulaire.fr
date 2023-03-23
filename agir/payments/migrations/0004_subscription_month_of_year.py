# Generated by Django 3.2.18 on 2023-03-23 12:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0003_payment_location_departement_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="subscription",
            name="month_of_year",
            field=models.PositiveSmallIntegerField(
                blank=True, editable=False, null=True, verbose_name="Mois de l'année"
            ),
        ),
    ]
