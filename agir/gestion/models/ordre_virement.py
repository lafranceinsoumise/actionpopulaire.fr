import logging

import dynamic_filenames
from django.db import models

from agir.gestion.models import Compte
from agir.lib.models import TimeStampedModel

logger = logging.getLogger(__name__)


class Statut(models.TextChoices):
    CREE = "C", "Créé"
    TRANSMIS = "T", "Transmis à la banque"
    VALIDE = "V", "Virement validé"


Statut_couleur = {
    Statut.CREE: "#6a89cc",
    Statut.VALIDE: "#78e08f",
    Statut.TRANSMIS: "#f6b93b",
}


class FichierOrdreDeVirement(TimeStampedModel):
    """
    Model représentant la génération d'un fichier d'ordre de virement depuis un
    fichier contenant un ensemble de virements avec son émetteur.
    """

    id = models.AutoField(primary_key=True, verbose_name="ID")

    nom = models.CharField(verbose_name="Nom", blank=False, max_length=255)
    statut = models.CharField(
        verbose_name="Statut", max_length=1, choices=Statut.choices, default=Statut.CREE
    )
    compte_emetteur = models.ForeignKey(
        Compte,
        verbose_name="Compte émetteur associé",
        null=False,
        blank=False,
        on_delete=models.deletion.CASCADE,
    )
    iban_copy = models.TextField(
        verbose_name="IBAN enregistré lors de la création de l'ordre de virement",
        blank=False,
        null=False,
    )
    bic_copy = models.TextField(
        verbose_name="BIC enregistré lors de la création de l'ordre de virement",
        blank=False,
        null=False,
    )
    nombre_transaction = models.IntegerField(
        verbose_name="Nombre de transaction pour l'ordre de virement",
        null=False,
    )
    montant_total = models.IntegerField(
        verbose_name="Montant total des transactions", null=False, blank=False
    )
    tableau_virement_file = models.FileField(
        verbose_name="Tableau des virements",
        null=True,
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="gestion/documents/ordre_de_virement/{instance.compte_emetteur}/{uuid:.2base32}-{uuid}{ext}"
        ),
    )
    tableau_virement_gsheet = models.URLField(
        verbose_name="Tableau GSheet",
        blank=True,
        null=True,
    )
    ordre_de_virement_out = models.FileField(
        verbose_name="Ordre de virement",
        null=True,
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="gestion/documents/ordre_de_virement/{instance.compte_emetteur}/{uuid:.2base32}-{uuid}{ext}"
        ),
    )

    def save(self, *args, **kwargs):
        if self.iban_copy is None or self.iban_copy == "":
            self.iban_copy = self.compte_emetteur.emetteur_iban
        if self.bic_copy is None or self.bic_copy == "":
            self.bic_copy = self.compte_emetteur.emetteur_bic
        super().save(*args, **kwargs)
