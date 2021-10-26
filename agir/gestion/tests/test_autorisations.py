from django.contrib.auth.models import Group
from hypothesis import given, assume, strategies as st
from hypothesis.extra.django import from_model, TestCase

from agir.gestion.models import Compte
from agir.gestion.models.common import Autorisation
from agir.gestion.rules import permission_sur_compte
from agir.lib.tests.strategies import person_with_role, printable_text


class RuleTestCase(TestCase):
    @given(person_with_role(), from_model(Compte), printable_text())
    def test_aucune_autorisation_par_defaut(self, person, compte, perm):
        perm_checker = permission_sur_compte(perm)
        self.assertFalse(perm_checker(person.role))
        self.assertFalse(perm_checker(person.role, obj=compte))

    @given(person_with_role(), from_model(Group), from_model(Compte), printable_text())
    def test_possible_ajouter_permission(self, person, group, compte, perm):
        group.user_set.add(person.role)
        Autorisation.objects.create(compte=compte, group=group, autorisations=[perm])

        perm_checker = permission_sur_compte(perm)
        self.assertFalse(perm_checker(person.role))
        self.assertTrue(perm_checker(person.role, obj=compte))

    @given(
        person_with_role(),
        from_model(Group),
        from_model(Compte),
        st.lists(printable_text()),
        printable_text(),
    )
    def test_autorisation_limitee_aux_roles_listes(
        self, person, group, compte, perms, other_perm
    ):
        assume(other_perm not in perms)

        group.user_set.add(person.role)
        Autorisation.objects.create(compte=compte, group=group, autorisations=perms)

        perm_checker = permission_sur_compte(other_perm)
        self.assertFalse(perm_checker(person.role, obj=compte))


class PermissionsTestCase(TestCase):
    @given(person_with_role(), from_model(Compte))
    def test_pas_de_permissions_par_defaut(self, person, compte):
        for perm, _ in Compte._meta.permissions:
            self.assertFalse(person.role.has_perm(f"gestion.{perm}", obj=compte))

    @given(
        person_with_role(),
        from_model(Compte),
        from_model(Group),
        st.lists(
            st.sampled_from([p for p, _ in Compte._meta.permissions]), unique=True
        ),
    )
    def test_peut_avoir_permission(self, person, compte, group, perms):
        group.user_set.add(person.role)

        Autorisation.objects.create(compte=compte, group=group, autorisations=perms)

        for perm in perms:
            self.assertTrue(
                person.role.has_perm(f"gestion.{perm}", obj=compte),
                f"{person} n'a pas {perm} sur {compte}",
            )

        for perm in set(p for p, _ in Compte._meta.permissions).difference(perms):
            self.assertFalse(person.role.has_perm(f"gestion.{perm}", obj=compte))
