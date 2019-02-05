# Generated by Django 2.1.5 on 2019-02-05 17:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("donations", "0009_auto_20190125_1516")]

    operations = [
        migrations.AlterField(
            model_name="operation",
            name="group",
            field=models.ForeignKey(
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="operations",
                related_query_name="operation",
                to="groups.SupportGroup",
            ),
        )
    ]
