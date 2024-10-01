from django.core.exceptions import ValidationError
from django.urls import reverse
from pathlib import Path


from agir.gestion.models import Compte
from agir.gestion.models.ordre_virement import FichierOrdreDeVirement
from agir.lib.tests.strategies import TestCase


class TestOrdreDeVirementTestCase(TestCase):

    def test_colonne_manquante_alert_utilisateur(self):
        compte = Compte.objects.create(
            designation="LFI",
            nom="La France Insoumise",
            emetteur_iban="FR7010096000502581761548M79",
        )
        with open(Path(__file__).parent / "test_missing_colonne.xlsx", "rb") as file:
            ordre_de_virement = FichierOrdreDeVirement()
            ordre_de_virement.tableau_virement_file = file
            ordre_de_virement.nom = "Test"
            ordre_de_virement.compte_emetteur = compte
            with self.assertRaises(ValidationError):
                ordre_de_virement.generer_fichier_ordre_virement()
