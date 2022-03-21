from django.urls import reverse
from hypothesis import given, strategies as st, settings
from hypothesis.extra.django import from_model, TestCase

from agir.gestion.tests.strategies import depense, projet, compte
from agir.lib.tests.strategies import person_with_role

admin_user = person_with_role(role__is_superuser=True, role__is_staff=True)

liste_depense_meme_compte = compte().flatmap(
    lambda c: st.lists(depense(compte=c), max_size=5)
)


class BaseAdminTestCase(TestCase):
    def admin_login(self, p):
        self.client.force_login(p.role, backend="agir.people.backend.PersonBackend")


class DepenseAdminTestCase(BaseAdminTestCase):
    @settings(deadline=1000)
    @given(admin_user, liste_depense_meme_compte)
    def test_peut_voir_la_liste(self, p, depenses):
        self.admin_login(p)
        res = self.client.get(
            reverse("admin:gestion_depense_changelist", urlconf="agir.api.admin_urls")
        )

        self.assertEqual(res.status_code, 200)

    @settings(deadline=1000)
    @given(admin_user, depense())
    def test_peut_voir_page_changement(self, p, depense):
        self.admin_login(p)

        res = self.client.get(
            reverse("admin:gestion_depense_change", args=(depense.id,))
        )

        self.assertEqual(res.status_code, 200)


class ProjetAdminTestCase(BaseAdminTestCase):
    def admin_login(self, p):
        self.client.force_login(p.role, backend="agir.people.backend.PersonBackend")

    @settings(deadline=1000)
    @given(admin_user, st.lists(projet(), max_size=3))
    def test_can_see_changelist(self, p, projets):
        self.admin_login(p)
        res = self.client.get(
            reverse("admin:gestion_projet_changelist", urlconf="agir.api.admin_urls")
        )

        self.assertEqual(res.status_code, 200)

    @settings(deadline=1000)
    @given(admin_user, projet())
    def test_peut_voir_page_changement(self, p, projet):
        self.admin_login(p)

        res = self.client.get(reverse("admin:gestion_projet_change", args=(projet.id,)))

        self.assertEqual(res.status_code, 200)
