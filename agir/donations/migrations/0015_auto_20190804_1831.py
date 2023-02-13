# Generated by Django 2.2.3 on 2019-08-04 16:31

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("donations", "0014_monthlyallocation_subscription")]

    operations = [
        migrations.AlterModelOptions(
            name="operation",
            options={"verbose_name": "Opération", "verbose_name_plural": "Opérations"},
        ),
        migrations.AlterModelOptions(
            name="spendingrequest",
            options={
                "permissions": (
                    ("review_spendingrequest", "Peut traiter les demandes de dépenses"),
                ),
                "verbose_name": "Demande de dépense",
                "verbose_name_plural": "Demandes de dépense",
            },
        ),
    ]
