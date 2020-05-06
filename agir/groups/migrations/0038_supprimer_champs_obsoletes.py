from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("groups", "0037_membership_type"),
    ]

    operations = [
        migrations.RemoveField(model_name="membership", name="is_manager",),
        migrations.RemoveField(model_name="membership", name="is_referent",),
    ]
