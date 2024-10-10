from decimal import Decimal

from hypothesis import strategies as st

from agir.gestion.models import Depense, Projet, Compte, Fournisseur
from agir.gestion.typologies import TypeDepense, TypeProjet
from agir.lib.tests.strategies import to_strategy, printable_text


@st.composite
def compte(draw, **kwargs):
    kwargs = {
        "designation": printable_text(min_size=1, max_size=5),
        "nom": printable_text(min_size=1, max_size=10),
        "description": printable_text(max_size=10),
        "beneficiaire_iban": "",
        "beneficiaire_bic": "",
        "emetteur_iban": "",
        "emetteur_bic": "",
        **kwargs,
    }

    return Compte.objects.create(**{k: draw(to_strategy(v)) for k, v in kwargs.items()})


@st.composite
def depense(draw, **kwargs):
    kwargs = {
        "titre": printable_text(min_size=1, max_size=10),
        "description": printable_text(max_size=10),
        "etat": st.sampled_from(Depense.Etat.values),
        "compte": compte(),
        "projet": st.one_of(st.just(None), projet()),
        "type": st.sampled_from(TypeDepense.values),
        "montant": st.decimals(
            min_value=Decimal("0.01"),
            max_value=Decimal("100000.00"),
            places=2,
            allow_nan=False,
            allow_infinity=False,
        ),
        "date_depense": st.dates(),
        **kwargs,
    }

    return Depense.objects.create(
        **{k: draw(to_strategy(v)) for k, v in kwargs.items()}
    )


@st.composite
def projet(draw, **kwargs):
    kwargs = {
        "titre": printable_text(min_size=1, max_size=10),
        "type": st.sampled_from(TypeProjet.values),
        "origine": st.sampled_from(Projet.Origin.values),
        "etat": st.sampled_from(Projet.Etat.values),
        "description": printable_text(max_size=10),
        **kwargs,
    }

    return Projet.objects.create(**{k: draw(to_strategy(v)) for k, v in kwargs.items()})


@st.composite
def fournisseur(draw, **kwargs):
    kwargs = {
        "nom": printable_text(min_size=1, max_size=10),
        "location_city": printable_text(min_size=1, max_size=10),
        "location_country": "FR",
        **kwargs,
    }

    f = Fournisseur(**{k: draw(to_strategy(v)) for k, v in kwargs.items()})

    f.save()
    return f
