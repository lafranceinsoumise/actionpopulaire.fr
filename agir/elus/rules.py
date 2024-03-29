import rules

from .models import Autorisation
from .models.mandats import StatutMandat, types_elus
from .models.parrainages import AccesApplicationParrainages
from ..lib.rules import is_authenticated_person
from ..people.models import Person


@rules.predicate
def est_elu_verifie(role, obj=None):
    if role.person.membre_reseau_elus in [
        Person.MEMBRE_RESEAU_NON,
        Person.MEMBRE_RESEAU_EXCLUS,
    ]:
        return False
    return any(
        model.objects.filter(person=role.person, statut=StatutMandat.CONFIRME).exists()
        for model in types_elus.values()
    )


@rules.predicate
def est_signataire_appel(role, obj=None):
    return "mandat" in role.person.meta.get("subscriptions", {}).get("NSP", {})


@rules.predicate
def a_acces_application(role, obj=None):
    return AccesApplicationParrainages.objects.filter(
        person=role.person, etat=AccesApplicationParrainages.Etat.VALIDE
    ).exists()


@rules.predicate
def acces_lecture_candidature(role, obj=None):
    if obj is None:
        return False

    code_circo = obj.circonscription.code
    potential_prefixes = [code_circo[:i] for i in range(len(code_circo) + 1)]

    return Autorisation.objects.filter(
        groupe__user=role,
        scrutin=obj.scrutin,
        prefixes__overlap=potential_prefixes,
    ).exists()


@rules.predicate
def acces_ecriture_candidature(role, obj=None):
    if obj is None:
        return False

    code_circo = obj.circonscription.code
    potential_prefixes = [code_circo[:i] for i in range(len(code_circo) + 1)]

    return (
        obj is not None
        and Autorisation.objects.filter(
            groupe__user=role,
            scrutin=obj.scrutin,
            ecriture=True,
            prefixes__overlap=potential_prefixes,
        ).exists()
    )


rules.add_perm(
    "elus.acces_parrainages",
    is_authenticated_person
    & (a_acces_application | (est_elu_verifie & est_signataire_appel)),
)

rules.add_perm(
    "elus.view_candidature", is_authenticated_person & acces_lecture_candidature
)

rules.add_perm(
    "elus.change_candidature", is_authenticated_person & acces_ecriture_candidature
)
