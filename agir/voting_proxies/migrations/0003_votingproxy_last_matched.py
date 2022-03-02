# Generated by Django 3.2.12 on 2022-03-02 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("voting_proxies", "0002_blankable_polling_station_number_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="votingproxy",
            name="last_matched",
            field=models.DateTimeField(
                editable=False,
                null=True,
                verbose_name="date de la dernière proposition de procuration",
            ),
        ),
    ]
