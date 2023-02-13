# Generated by Django 2.1.7 on 2019-03-08 17:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("groups", "0001_creer_modeles"), ("mailing", "0001_initial")]

    operations = [
        migrations.RenameField(
            model_name="segment",
            old_name="support_group_status",
            new_name="supportgroup_status",
        ),
        migrations.AddField(
            model_name="segment",
            name="last_login",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Date de dernière connexion à la plateforme",
            ),
        ),
        migrations.AddField(
            model_name="segment",
            name="registration_date",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Date d'inscription à la plateforme"
            ),
        ),
        migrations.AddField(
            model_name="segment",
            name="supportgroup_subtypes",
            field=models.ManyToManyField(
                blank=True,
                to="groups.SupportGroupSubtype",
                verbose_name="Sous-types de groupes",
            ),
        ),
    ]
