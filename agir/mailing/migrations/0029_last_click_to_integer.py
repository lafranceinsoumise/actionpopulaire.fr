# Generated by Django 2.2.16 on 2020-10-01 15:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mailing", "0028_auto_20200924_1747"),
    ]

    operations = [
        migrations.RemoveField(model_name="segment", name="last_click"),
        migrations.RemoveField(
            model_name="segment",
            name="last_open",
        ),
        migrations.AddField(
            model_name="segment",
            name="last_click",
            field=models.IntegerField(
                blank=True,
                help_text="Indiquer le nombre de jours",
                null=True,
                verbose_name="Limiter aux personnes ayant cliqué dans un email envoyé au court des derniers jours",
            ),
        ),
        migrations.AddField(
            model_name="segment",
            name="last_open",
            field=models.IntegerField(
                blank=True,
                help_text="Indiquer le nombre de jours",
                null=True,
                verbose_name="Limiter aux personnes ayant ouvert un email envoyé au court de derniers jours",
            ),
        ),
    ]
