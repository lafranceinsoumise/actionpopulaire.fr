import decimal

from django.contrib.auth.models import Group, Permission
from hypothesis import given, strategies as st

from agir.gestion.models import Compte, Depense, Autorisation
from agir.gestion.models.depenses import etat_initial
from agir.gestion.typologies import TypeDepense
from agir.lib.tests.strategies import TestCase
from agir.people.models import Person

MONTANT_MAX = decimal.Decimal("99999999.99")

types_depense_compatibles = st.sampled_from(TypeDepense.values).flatmap(
    lambda type_parent: st.sampled_from(
        [v for v in TypeDepense.values if v.startswith(type_parent)]
    ).map(lambda type_enfant: (type_parent, type_enfant))
)


@st.composite
def decimaux_croissants(draw, min_value="0.00", max_value=MONTANT_MAX, equal=True):
    borne_sup_petit = max_value
    if not equal:
        borne_sup_petit -= decimal.Decimal("0.01")

    petit = draw(
        st.decimals(
            min_value=min_value,
            max_value=borne_sup_petit,
            places=2,
            allow_nan=False,
            allow_infinity=False,
        )
    )

    borne_inf_grand = petit
    if not equal:
        borne_inf_grand += decimal.Decimal("0.01")

    grand = draw(
        st.decimals(
            min_value=borne_inf_grand,
            max_value=max_value,
            places=2,
            allow_nan=False,
            allow_infinity=False,
        )
    )

    return (petit, grand)


class EngagementDepenseTestCase(TestCase):
    def setUp(self) -> None:
        self.compte = Compte.objects.create(
            designation="LFI",
            nom="La France insoumise",
        )

        self.person = Person.objects.create_person("a@b.c", create_role=True)

        self.group = Group.objects.create(name="groupe")
        Permission.objects.get(codename="gerer_depense").group_set.add(self.group)
        self.group.user_set.add(self.person.role)

    def test_creation_dans_etat_attente_engagement(self):
        d = Depense(
            titre="Ma dépense",
            compte=self.compte,
            type=TypeDepense.FRAIS_RECEPTION_HEBERGEMENT,
            montant=45.20,
        )

        self.assertEqual(
            etat_initial(d, self.person.role), Depense.Etat.ATTENTE_ENGAGEMENT
        )

    def test_creation_dans_etat_attente_engagement_avec_permission(self):
        Autorisation.objects.create(
            compte=self.compte, group=self.group, autorisations=["engager_depense"]
        )
        d = Depense(
            titre="Ma dépense",
            compte=self.compte,
            type=TypeDepense.FRAIS_RECEPTION_HEBERGEMENT,
            montant=45.20,
        )

        self.assertEqual(etat_initial(d, self.person.role), Depense.Etat.CONSTITUTION)

    @given(
        types_depense_compatibles,
        decimaux_croissants(),
    )
    def test_creation_sous_plafond_engagement(self, types_depense, montants):
        type_parent, type_enfant = types_depense
        montant_depense, plafond = montants

        self.compte.engagement_automatique[type_parent] = plafond
        self.compte.save()

        self.assertTrue(self.person.has_perm("gestion.gerer_depense"))

        d = Depense(
            titre="Ma dépense !",
            compte=self.compte,
            type=type_enfant,
            montant=montant_depense,
        )

        self.assertEqual(etat_initial(d, self.person.role), Depense.Etat.CONSTITUTION)

    @given(
        types_depense_compatibles,
        decimaux_croissants(equal=False),
    )
    def test_creation_au_dessus_plafond_sans_engagement(self, types_depense, montants):
        type_parent, type_enfant = types_depense
        plafond, montant_depense = montants

        self.compte.engagement_automatique[type_parent] = plafond
        self.compte.save()

        d = Depense(
            titre="Ma dépense !",
            compte=self.compte,
            type=type_enfant,
            montant=montant_depense,
        )

        self.assertEqual(
            etat_initial(d, self.person.role), Depense.Etat.ATTENTE_ENGAGEMENT
        )
