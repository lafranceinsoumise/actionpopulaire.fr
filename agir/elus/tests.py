from data_france.models import CollectiviteDepartementale, CollectiviteRegionale
from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from agir.elus.models import (
    AccesApplicationParrainages,
    StatutMandat,
    MandatMunicipal,
    MandatDepartemental,
    MandatRegional,
)
from agir.lib.tests.utils import import_communes_test_data
from agir.people.models import Person


class ViewsTestCase(TestCase):
    def setUp(self) -> None:
        import_communes_test_data()
        self.person = Person.objects.create_insoumise("a@b.c", create_role=True)
        self.client.force_login(self.person.role)

    def test_can_add_mandat_municipal(self):
        res = self.client.get(reverse("elus:creer_mandat_municipal"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(
            reverse("elus:creer_mandat_municipal"),
            data={
                "conseil": "COM-00001",
                "mandat": MandatMunicipal.MANDAT_CONSEILLER_OPPOSITION,
                "communautaire": MandatMunicipal.MANDAT_EPCI_OPPOSITION,
                "dates_1": "28/06/2020",
                "dates_2": "31/03/2026",
                "id_delegations_10": "Y",
                "membre_reseau_elus": Person.MEMBRE_RESEAU_SOUHAITE,
            },
        )
        self.assertRedirects(res, reverse("mandats"))

        self.assertTrue(MandatMunicipal.objects.filter(person=self.person).exists())

    def test_can_add_mandat_departemental(self):
        res = self.client.get(reverse("elus:creer_mandat_departemental"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(
            reverse("elus:creer_mandat_departemental"),
            data={
                "conseil": CollectiviteDepartementale.objects.get(code="01D").id,
                "mandat": MandatDepartemental.MANDAT_PRESIDENT,
                "dates_1": "28/06/2020",
                "dates_2": "31/03/2026",
                "membre_reseau_elus": Person.MEMBRE_RESEAU_SOUHAITE,
            },
        )
        self.assertRedirects(res, reverse("mandats"))

        self.assertTrue(MandatDepartemental.objects.filter(person=self.person).exists())

    def test_can_add_mandat_regional(self):
        res = self.client.get(reverse("elus:creer_mandat_regional"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(
            reverse("elus:creer_mandat_regional"),
            data={
                "conseil": CollectiviteRegionale.objects.get(code="01R").id,
                "mandat": MandatRegional.MANDAT_CONSEILLER_MAJORITE,
                "dates_1": "28/06/2020",
                "dates_2": "31/03/2026",
                "membre_reseau_elus": Person.MEMBRE_RESEAU_SOUHAITE,
            },
        )
        self.assertRedirects(res, reverse("mandats"))

        self.assertTrue(MandatRegional.objects.filter(person=self.person).exists())

    def test_peut_editer_mandat_sans_conseil(self):
        mandat = MandatMunicipal.objects.create(
            person=self.person, mandat=MandatMunicipal.MANDAT_MAIRE
        )

        res = self.client.get(
            reverse("elus:modifier_mandat_municipal", args=(mandat.id,))
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(
            reverse("elus:modifier_mandat_municipal", args=(mandat.id,)),
            data={
                "mandat": MandatMunicipal.MANDAT_CONSEILLER_OPPOSITION,
                "communautaire": MandatMunicipal.MANDAT_EPCI_OPPOSITION,
                "dates_1": "28/06/2020",
                "dates_2": "31/03/2026",
                "id_delegations_10": "Y",
                "membre_reseau_elus": Person.MEMBRE_RESEAU_SOUHAITE,
            },
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFormError(res, "form", "conseil", "Ce champ est obligatoire.")

        res = self.client.post(
            reverse("elus:modifier_mandat_municipal", args=(mandat.id,)),
            data={
                "conseil": "COM-00002",
                "mandat": MandatMunicipal.MANDAT_CONSEILLER_OPPOSITION,
                "communautaire": MandatMunicipal.MANDAT_EPCI_OPPOSITION,
                "dates_1": "28/06/2020",
                "dates_2": "31/03/2026",
                "id_delegations_10": "Y",
                "membre_reseau_elus": Person.MEMBRE_RESEAU_SOUHAITE,
            },
        )
        self.assertRedirects(res, reverse("mandats"))

        mandat.refresh_from_db()
        self.assertEqual(mandat.conseil.code, "00002")


class AccesParrainagesTestCase(TestCase):
    def test_acces_impossible_par_defaut(self):
        p = Person.objects.create_insoumise(email="test@dom.fr", create_role=True)
        self.client.force_login(p.role)

        res = self.client.get(reverse("elus:parrainages"))
        self.assertRedirects(res, reverse("elus:demande_acces_parrainages"))

    def test_acces_elus_signataires_appel(self):
        p = Person.objects.create_person(
            email="conseiller@mairie.fr",
            create_role=True,
            meta={"subscriptions": {"NSP": {"mandat": "municipal"}}},
        )
        self.client.force_login(p.role)

        MandatMunicipal.objects.create(
            person=p,
            statut=StatutMandat.CONFIRME,
        )

        res = self.client.get(reverse("elus:parrainages"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_acces_avec_acces_explicite(self):
        p = Person.objects.create_person(
            email="volontaire@groupe.fr",
            create_role=True,
        )
        self.client.force_login(p.role)

        AccesApplicationParrainages.objects.create(
            person=p, etat=AccesApplicationParrainages.Etat.VALIDE
        )

        res = self.client.get(reverse("elus:parrainages"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_formulaire_redigire_app_si_deja_autorise(self):
        p = Person.objects.create_person(
            email="volontaire@groupe.fr",
            create_role=True,
        )
        self.client.force_login(p.role)

        AccesApplicationParrainages.objects.create(
            person=p, etat=AccesApplicationParrainages.Etat.VALIDE
        )

        res = self.client.get(reverse("elus:demande_acces_parrainages"))
        self.assertRedirects(res, reverse("elus:parrainages"))


class DemandeAccesParrainagesTestCase(TestCase):
    def test_creation_demande_acces(self):
        p = Person.objects.create_person("volontaire@groupe.fr", create_role=True)
        self.client.force_login(p.role)

        url = reverse("elus:demande_acces_parrainages")

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(
            url,
            {
                "first_name": "Philippe",
                "last_name": "Edouard",
                "contact_phone": "06 98 23 45 23",
                "location_zip": "95000",
                "location_city": "Cergy",
                "engagement": "Y",
            },
        )

        self.assertRedirects(res, reverse("dashboard"), fetch_redirect_response=False)

        self.assertTrue(
            AccesApplicationParrainages.objects.filter(
                person=p, etat=AccesApplicationParrainages.Etat.EN_ATTENTE
            )
        )

        res = self.client.get(reverse("dashboard"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        msgs = list(res.context["messages"])
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS)
