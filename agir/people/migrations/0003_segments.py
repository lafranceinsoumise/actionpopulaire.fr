from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0002_objets_initiaux"),
        ("nuntius", "0015_only_one_segment_model"),
        migrations.swappable_dependency(settings.NUNTIUS_SEGMENT_MODEL),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="role",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="person",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="personform",
            name="segment",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="person_forms",
                related_query_name="person_form",
                to=settings.NUNTIUS_SEGMENT_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="personform",
            name="campaign_template",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="nuntius.campaign",
                verbose_name="Créer une campagne à partir de ce modèle",
            ),
        ),
    ]
