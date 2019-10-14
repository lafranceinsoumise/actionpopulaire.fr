# Generated by Django 2.2.5 on 2019-10-08 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("payments", "0016_auto_20190821_1132")]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="status",
            field=models.IntegerField(
                choices=[
                    (0, "En attente"),
                    (1, "Terminé"),
                    (2, "Abandonné"),
                    (3, "Annulé"),
                    (4, "Refusé"),
                    (-1, "Remboursé"),
                ],
                default=0,
                verbose_name="status",
            ),
        )
    ]
