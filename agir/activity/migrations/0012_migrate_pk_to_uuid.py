from __future__ import unicode_literals
import uuid

import django
from django.db import migrations, models


def fill_uuids(apps, schema_editor):
    Announcement = apps.get_model("activity", "Announcement")
    for obj in Announcement.objects.all():
        obj.uuid = uuid.uuid4()
        obj.save()


def update_foreignkeys(apps, schema_editor):
    Announcement = apps.get_model("activity", "Announcement")
    Activity = apps.get_model("activity", "Activity")
    for obj in Announcement.objects.all():
        Activity.objects.filter(announcement=obj).update(announcement_uuid=obj.uuid)


def reverse_update_foreignkeys(apps, schema_editor):
    Announcement = apps.get_model("activity", "Announcement")
    Activity = apps.get_model("activity", "Activity")
    for obj in Announcement.objects.all():
        Activity.objects.filter(announcement_uuid=obj.uuid).update(announcement=obj)


class Migration(migrations.Migration):
    """ Change model with integer pk to UUID pk.
    """

    dependencies = [("activity", "0011_auto_20201217_1625")]

    operations = [
        migrations.AddField(
            model_name="announcement", name="uuid", field=models.UUIDField(null=True)
        ),
        migrations.RunPython(fill_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="announcement",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, serialize=False, editable=False, unique=True
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="announcement_uuid",
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(update_foreignkeys, reverse_update_foreignkeys),
        migrations.RemoveField("Activity", "announcement"),
        migrations.RenameField(
            model_name="activity", old_name="announcement_uuid", new_name="announcement"
        ),
        migrations.RemoveField("Announcement", "id"),
        migrations.RenameField(
            model_name="announcement", old_name="uuid", new_name="id"
        ),
        migrations.AlterField(
            model_name="announcement",
            name="id",
            field=models.UUIDField(
                primary_key=True,
                default=uuid.uuid4,
                serialize=False,
                editable=False,
                help_text="UUID interne à l'API pour identifier la ressource",
                verbose_name="UUID",
            ),
        ),
        migrations.AlterField(
            model_name="activity",
            name="announcement",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="activities",
                related_query_name="activity",
                to="activity.announcement",
            ),
        ),
        migrations.AddField(
            model_name="announcement",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                editable=False,
                verbose_name="date de création",
            ),
        ),
        migrations.AddField(
            model_name="announcement",
            name="modified",
            field=models.DateTimeField(
                auto_now=True, verbose_name="dernière modification"
            ),
        ),
        migrations.AddField(
            model_name="announcement",
            name="custom_display",
            field=models.SlugField(
                blank=True,
                help_text="Ce champ sert au pôle outils numériques",
                verbose_name="Affichage personnalisé",
            ),
        ),
    ]
