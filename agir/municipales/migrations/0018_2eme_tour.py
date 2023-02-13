from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("municipales", "0017_auto_20200326_1829"),
    ]

    operations = [
        migrations.RenameField(
            model_name="communepage",
            old_name="strategy",
            new_name="liste_tour_1",
        ),
        migrations.AlterField(
            model_name="communepage",
            name="liste_tour_1",
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name="Nom de la liste du 1er tour",
            ),
        ),
        migrations.RenameField(
            model_name="communepage",
            old_name="tete_liste",
            new_name="tete_liste_tour_1",
        ),
        migrations.AlterField(
            model_name="communepage",
            name="tete_liste_tour_1",
            field=models.CharField(
                blank=True,
                help_text="Le nom de la tête de liste, tel qu'il s'affichera publiquement",
                max_length=255,
                verbose_name="Nom de la tête de liste au 1er tour",
            ),
        ),
        migrations.AddField(
            model_name="communepage",
            name="liste_tour_2",
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name="Nom de la liste du 2e tour",
            ),
        ),
        migrations.AddField(
            model_name="communepage",
            name="tete_liste_tour_2",
            field=models.CharField(
                blank=True,
                help_text="Le nom de la tête de liste, tel qu'il s'affichera publiquement",
                max_length=255,
                verbose_name="Nom de la tête de liste au 2e tour",
            ),
        ),
        migrations.RenameField(
            model_name="communepage",
            old_name="municipales2020_admins",
            new_name="chefs_file",
        ),
    ]
