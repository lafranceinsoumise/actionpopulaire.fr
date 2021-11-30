# Generated by Django 3.1.13 on 2021-11-16 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestion", "0007_projet_titre_plus_long"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="type",
            field=models.CharField(
                choices=[
                    ("DEV", "Devis"),
                    ("CON", "Contrat"),
                    ("FAC", "Facture"),
                    ("JUS", "Justificatif de dépense"),
                    ("JUS-BIL", "Billet de train"),
                    ("JUS-TRAIN", "Justificatif de train"),
                    ("JUS-CEM", "Carte d'embarquement"),
                    ("PAY", "Preuve de paiement"),
                    ("PAY-CHK", "Scan du chèque"),
                    ("PAY-TKT", "Ticket de caisse"),
                    ("EXA", "Exemplaire fourni"),
                    ("EXA-BAT", "BAT"),
                    ("EXA-TRA", "Tract"),
                    ("EXA-AFF", "Affiche"),
                    ("PHO", "Photographie de l'objet ou de l'événement"),
                    ("AUT", "Autre (à détailler dans les commentaires)"),
                    ("ATT", "Attestation"),
                    ("ATT-GRA", "Attestation de gratuité"),
                    ("ATT-CON", "Attestation de concours en nature"),
                    ("ATT-REG", "Attestation de réglement des consommations"),
                    (
                        "ATT-ESP",
                        "Demande d'autorisation d'occupation de l'espace public",
                    ),
                ],
                max_length=10,
                verbose_name="Type de document",
            ),
        ),
        migrations.AlterField(
            model_name="projet",
            name="origine",
            field=models.CharField(
                choices=[
                    ("A", "Créé sur l'admin"),
                    ("U", "Créé par un·e militant·e sur Action Populaire"),
                    ("R", "Réunion publique suite à demande"),
                ],
                default="A",
                editable=False,
                max_length=1,
                verbose_name="Origine du projet",
            ),
        ),
    ]
