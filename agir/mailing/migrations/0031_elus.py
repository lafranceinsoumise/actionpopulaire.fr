# Generated by Django 2.2.16 on 2020-10-05 13:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mailing", "0030_segment_draw_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="segment",
            name="elu_departemental",
            field=models.BooleanField(
                default=True, verbose_name="Avec un mandat départemental"
            ),
        ),
        migrations.AddField(
            model_name="segment",
            name="elu_municipal",
            field=models.BooleanField(
                default=True, verbose_name="Avec un mandat municipal"
            ),
        ),
        migrations.AddField(
            model_name="segment",
            name="elu_regional",
            field=models.BooleanField(
                default=True, verbose_name="Avec un mandat régional"
            ),
        ),
        migrations.AddField(
            model_name="segment",
            name="elu",
            field=models.CharField(
                choices=[
                    ("N", "Non"),
                    ("M", "Membre du réseau des élus"),
                    ("R", "Référencé comme élu, non exclus"),
                ],
                default="N",
                max_length=1,
                verbose_name="Est un élu",
            ),
        ),
    ]
