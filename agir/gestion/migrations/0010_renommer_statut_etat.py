from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion", "0009_auto_20210526_1807"),
    ]

    operations = [
        migrations.RenameField(
            model_name="projet", old_name="statut", new_name="etat",
        ),
        migrations.AlterModelOptions(
            name="compte",
            options={
                "permissions": [
                    (
                        "acces_contenu_restreint",
                        "Voir les projets, dépenses et documents dont l'accès est indiqué comme restreint.",
                    ),
                    (
                        "acces_contenu_secret",
                        "Voir les projets, dépenses et documents dont l'accès est indiqué commme secret.",
                    ),
                    ("engager_depense", "Engager une dépense pour ce compte"),
                    ("gerer_depense", "Gérer les dépenses"),
                    ("controler_depense", "Contrôler les dépenses"),
                    ("gerer_projet", "Gérer les projets"),
                    ("contrôler_projet", "Contrôler les projets"),
                ],
                "verbose_name": "Compte",
                "verbose_name_plural": "Comptes",
            },
        ),
        migrations.AlterField(
            model_name="projet",
            name="etat",
            field=models.CharField(
                choices=[
                    ("DFI", "Demande de financement"),
                    ("REF", "Refusé"),
                    ("ECO", "En cours de constitution"),
                    ("FIN", "Finalisé par le secrétariat"),
                    ("REN", "Renvoyé par l'équipe financière"),
                    ("CLO", "Clôturé"),
                ],
                max_length=3,
                verbose_name="Statut",
            ),
        ),
    ]
