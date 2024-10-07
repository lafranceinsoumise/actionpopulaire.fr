import logging

import dynamic_filenames
import pandas as pd
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models

from agir.gestion.admin.ordre_de_virement_utils import extract_virements
from agir.gestion.models import Compte
from agir.gestion.virements import generer_fichier_virement, Partie
from agir.lib.iban import IBAN
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

ORDRE_DE_VIREMENT_NECESSARY_KEYS = [
    "MONTANT",
    "NOM BENEFICIAIRE",
    "IBAN BENEFICIAIRE",
    "MOTIF",
]


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

    def get_iban_debiteur_from_excel(self, df):
        iban = None
        try:
            iban_debiteur_col = df["IBAN Débiteur"]
            iban = iban_debiteur_col[0]
        except KeyError:
            pass
        return iban

    def setupIbanBic(self, iban, bic):
        if self.iban_copy is None or self.iban_copy == "":
            self.iban_copy = iban
        if self.bic_copy is None or self.bic_copy == "":
            self.bic_copy = bic

    def generer_fichier_ordre_virement(self):
        if self.tableau_virement_file is None:
            raise ValidationError("Fichier inexistant pour générer l'ordre de virement")
        df = pd.read_excel(self.tableau_virement_file)
        missing_columns = [
            column for column in ORDRE_DE_VIREMENT_NECESSARY_KEYS if column not in df
        ]
        if len(missing_columns) > 0:
            raise ValidationError(
                f"Colonne(s) manquante(s) : {', '.join(missing_columns)}"
            )
        self.montant_total = df["MONTANT"].sum() * 100
        self.nombre_transaction = df["MONTANT"].count()
        iban_from_excel = self.get_iban_debiteur_from_excel(df)
        virements = extract_virements(df)
        emetteur_iban = self.compte_emetteur.emetteur_iban
        if (emetteur_iban is None or emetteur_iban is "") and iban_from_excel is None:
            raise ValidationError("L'emetteur n'a pas de IBAN, merci d'en ajouter un.")

        iban = (
            IBAN(iban_from_excel)
            if iban_from_excel is not None
            else self.compte_emetteur.emetteur_iban
        )
        self.setupIbanBic(iban.value, iban.bic)
        emetteur = Partie(
            nom=self.compte_emetteur.designation,
            iban=iban,
            bic=self.compte_emetteur.emetteur_bic,
            label=self.compte_emetteur.nom.upper(),
        )

        ordre_virement_contenu = generer_fichier_virement(
            emetteur=emetteur,
            virements=virements,
        )
        self.ordre_de_virement_out = ContentFile(
            ordre_virement_contenu,
            name=self._meta.get_field("ordre_de_virement_out").generate_filename(
                self, f"ordre_virement_{self.id}.xml"
            ),
        )
