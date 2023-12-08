# Generated by Django 3.2.23 on 2023-11-21 14:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("donations", "0026_accountoperation"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="accountoperation",
            options={
                "verbose_name": "opération financière",
                "verbose_name_plural": "opérations financières",
            },
        ),
        migrations.AlterField(
            model_name="spendingrequest",
            name="category",
            field=models.CharField(
                choices=[
                    ("H", "[Obsolète] Matériel militant"),
                    ("S", "[Obsolète] Prestation de service"),
                    ("V", "[Obsolète] Location de salle"),
                    ("O", "[Obsolète] Autres"),
                    ("IM", "Impressions"),
                    ("CO", "Achat de consommables (colles, feutres, … )"),
                    (
                        "AC",
                        "Achat de matériel (quincaillerie, matériel de collage, … )",
                    ),
                    ("DE", "Déplacement"),
                    ("HE", "Hébergement"),
                    ("SA", "Location de salle"),
                    ("MA", "Location de matériel (mobilier, vaisselle, … )"),
                    ("TE", "Location de matériel technique (sono, vidéo)"),
                    ("VE", "Location de véhicule"),
                    ("AB", "Abonnement"),
                ],
                max_length=2,
                verbose_name="Catégorie",
            ),
        ),
    ]