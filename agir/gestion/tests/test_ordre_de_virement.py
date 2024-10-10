from io import BytesIO

import pandas as pd
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile
from django.urls import reverse
from pathlib import Path

from agir.gestion.admin import ImportTableauVirementsForm
from agir.gestion.models import Compte
from agir.gestion.models.ordre_virement import FichierOrdreDeVirement
from agir.lib.tests.strategies import TestCase


class TestOrdreDeVirementTestCase(TestCase):
    def setUp(self):
        self.compte = Compte.objects.create(
            designation="LFI",
            nom="La France Insoumise",
            emetteur_iban="FR7010096000502581761548M79",
        )

        self.post_data = {
            "nom": "Nom du virement",
            "emetteur": self.compte,
        }

    def test_invalid_file(self):
        content = b"Ceci n'est pas un fichier excel"

        f = ImportTableauVirementsForm(
            self.post_data,
            {"tableau_virement_file": ContentFile(content, "fichier.xlsx")},
        )
        self.assertFalse(f.is_valid())
        self.assertTrue(f.has_error("tableau_virement_file", "invalid_excel"))

    def test_colonne_manquante_alert_utilisateur(self):
        df = pd.DataFrame(
            [
                {
                    "MONTANT": 12,
                    "IBAN BENEFICIAIRE": "FR3217569000505572113917D97",
                    "NOM BENEFICIAIRE": "Salomé",
                }
            ]
        )
        c = BytesIO()
        df.to_excel(c, index=False, engine="openpyxl")

        f = ImportTableauVirementsForm(
            self.post_data,
            {"tableau_virement_file": ContentFile(c.getvalue(), "fichier.xlsx")},
        )

        self.assertFalse(f.is_valid())
        self.assertTrue(f.has_error("tableau_virement_file", "missing_columns"))

    def test_donnees_manquantes(self):
        df = pd.DataFrame(
            [
                {
                    "MONTANT": 12,
                    "IBAN BENEFICIAIRE": "FR3217569000505572113917D97",
                    "MOTIF": "",
                    "NOM BENEFICIAIRE": "Alexandra",
                },
                {
                    "MONTANT": 42,
                    "IBAN BENEFICIAIRE": "",
                    "MOTIF": "REMB DEP",
                    "NOM BENEFICIAIRE": "Benjamin",
                },
            ]
        )
        c = BytesIO()
        df.to_excel(c, engine="openpyxl")

        f = ImportTableauVirementsForm(
            self.post_data,
            {"tableau_virement_file": ContentFile(c.getvalue(), "fichier.xlsx")},
        )
        self.assertFalse(f.is_valid())
        self.assertTrue(f.has_error("tableau_virement_file", "missing_values"))
