from django.core.files.base import ContentFile
from django.utils import timezone
from hypothesis import given, strategies as st
from hypothesis.extra.django import TestCase

from agir.gestion.admin.forms import ReglementForm
from agir.gestion.models import Reglement
from agir.gestion.tests.strategies import depense, fournisseur
from agir.lib.tests.strategies import iban


class NouveauReglementFormTestCase(TestCase):
    @given(depense(), fournisseur(iban=iban("FR7010096000502581761548M79")))
    def test_preuve_interdite_pour_un_reglement_a_faire(self, depense, fournisseur):
        form_data = {
            "intitule": "Solde",
            "choix_mode": ReglementForm.VIREMENT_PLATEFORME,
            "montant": depense.montant,
            "date": timezone.now().date(),
            "fournisseur": fournisseur.id,
            "location_country_fournisseur": "FR",
        }
        fichier = ContentFile(b"Faux fichier !")
        fichier.name = "fichier.txt"

        f = ReglementForm(
            depense=depense,
            data=form_data,
            files={
                "preuve": fichier,
            },
        )

        self.assertIn("preuve", f.errors)
        self.assertEqual(f.errors.as_data()["preuve"][0].code, "preuve_interdite")

    @given(depense(), fournisseur(iban=iban()))
    def test_programmer_virement(self, depense, fournisseur):
        form_data = {
            "intitule": "Solde",
            "choix_mode": ReglementForm.VIREMENT_PLATEFORME,
            "montant": depense.montant,
            "date": timezone.now().date(),
            "fournisseur": fournisseur.id,
            "location_country_fournisseur": "FR",
        }

        f = ReglementForm(depense=depense, data=form_data)
        self.assertTrue(f.is_valid())

        r = f.save()

        self.assertEqual(r.etat, Reglement.Etat.ATTENTE)
        self.assertEqual(r.mode, Reglement.Mode.VIREMENT)

    @given(depense(), fournisseur(iban=""), st.sampled_from(Reglement.Mode.values))
    def test_enregistrer_reglement(self, depense, fournisseur, mode):
        form_data = {
            "intitule": "Solde",
            "choix_mode": mode,
            "montant": depense.montant,
            "date": timezone.now().date(),
            "fournisseur": fournisseur.id,
            "location_country_fournisseur": "FR",
        }
        preuve = ContentFile(b"Preuve de paiement impressionante !")
        preuve.name = "preuve-paiement.txt"

        f = ReglementForm(depense=depense, data=form_data, files={"preuve": preuve})

        self.assertTrue(f.is_valid())

        r = f.save()

        self.assertEqual(r.mode, mode)
        self.assertEqual(r.etat, Reglement.Etat.REGLE)
