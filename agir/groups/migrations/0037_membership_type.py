# Generated by Django 2.2.12 on 2020-04-24 13:07

from django.db import migrations, models
from django.db.models.expressions import RawSQL


def bools_vers_choices(apps, schema):
    Membership = apps.get_model("groups", "Membership")
    Membership.objects.filter(
        models.Q(is_referent=True) | models.Q(is_manager=True)
    ).update(
        membership_type=models.Case(
            models.When(models.Q(is_referent=True), then=100),
            default=50,
            output_field=models.IntegerField(),
        )
    )


def choices_vers_bools(apps, schema):
    Membership = apps.get_model("groups", "Membership")
    Membership.objects.filter(membership_type__gte=50).update(
        is_manager=True,
        is_referent=models.Case(
            models.When(models.Q(membership_type__gte=100), then=True), default=False
        ),
    )


class Migration(migrations.Migration):

    dependencies = [
        ("groups", "0036_recherche_plein_texte"),
    ]

    operations = [
        migrations.AddField(
            model_name="membership",
            name="membership_type",
            field=models.IntegerField(
                choices=[
                    (10, "Membre du groupe"),
                    (50, "Membre gestionnaire"),
                    (100, "Animateur⋅rice"),
                ],
                default=10,
                verbose_name="Statut dans le groupe",
            ),
        ),
        migrations.RunPython(code=bools_vers_choices, reverse_code=choices_vers_bools),
        migrations.RemoveField(model_name="membership", name="is_manager",),
        migrations.RemoveField(model_name="membership", name="is_referent",),
    ]
