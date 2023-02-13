# Generated by Django 3.1.13 on 2021-07-26 14:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("data_france", "0029_deputes_europeens"),
        ("elus", "0029_mandatdeputeeuropeen"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="rechercheparrainage",
            name="parrainage_un_seul_elu",
        ),
        migrations.AddField(
            model_name="rechercheparrainage",
            name="depute_europeen",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="parrainages",
                related_query_name="parrainage",
                to="data_france.deputeeuropeen",
                verbose_name="Député·e européen·e",
            ),
        ),
        migrations.AddField(
            model_name="rechercheparrainage",
            name="elu_regional",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="parrainages",
                related_query_name="parrainage",
                to="data_france.eluregional",
                verbose_name="Élu·e régional·e",
            ),
        ),
        migrations.AddConstraint(
            model_name="rechercheparrainage",
            constraint=models.UniqueConstraint(
                condition=models.Q(_negated=True, statut=5),
                fields=("elu_regional",),
                name="parrainage_un_seul_actif_elu_regional",
            ),
        ),
        migrations.AddConstraint(
            model_name="rechercheparrainage",
            constraint=models.UniqueConstraint(
                condition=models.Q(_negated=True, statut=5),
                fields=("depute_europeen",),
                name="parrainage_un_seul_actif_depute_europeen",
            ),
        ),
        migrations.AddConstraint(
            model_name="rechercheparrainage",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("elu_departemental__isnull", False),
                        ("maire__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("elu_regional__isnull", False),
                        ("maire__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("depute__isnull", False),
                        ("maire__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("depute_europeen__isnull", False),
                        ("maire__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("elu_departemental__isnull", False),
                        ("elu_regional__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("depute__isnull", False),
                        ("elu_departemental__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("depute_europeen__isnull", False),
                        ("elu_departemental__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("depute__isnull", False),
                        ("elu_regional__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("depute_europeen__isnull", False),
                        ("elu_regional__isnull", False),
                        _negated=True,
                    ),
                    models.Q(
                        ("depute__isnull", False),
                        ("depute_europeen__isnull", False),
                        _negated=True,
                    ),
                ),
                name="parrainage_un_seul_elu",
            ),
        ),
    ]
