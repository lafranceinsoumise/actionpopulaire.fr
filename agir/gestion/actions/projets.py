from typing import Dict, List, Tuple

from django.db.models import Q

from agir.gestion.actions import Condition, NiveauTodo
from agir.gestion.models import Participation, Projet
from agir.gestion.typologies import TypeProjet, TypeDocument, TypeDepense
from agir.people.models import Person


def verifier_transports(projet: Projet):
    intervenants = projet.participations.values_list("person_id", flat=True)

    transportes = Person.objects.filter(
        depense__projet_id=projet.pk, depense__type__startswith=TypeDepense.TRANSPORTS
    ).values_list("id", flat=True)

    return not intervenants.difference(transportes).exists()


def verifier_hebergement(projet: Projet):
    intervenants = projet.participations.values_list(
        "person_id", flat=True
    ).difference()

    heberges = Person.objects.filter(
        depense__projet_id=projet.pk,
        depense__type__startswith=TypeDepense.FRAIS_RECEPTION_HEBERGEMENT,
    ).values_list("id", flat=True)

    return not intervenants.difference(heberges).exists()


validation_conditions: Dict[TypeProjet, List[Condition]] = {
    TypeProjet.CONFERENCE_PRESSE: [
        Condition(
            Q(
                participation__role__in=[
                    Participation.Role.ORATEUR,
                    Participation.Role.CANDIDAT,
                ]
            ),
            "La conférence de presse doit identifier les intervenants, orateurs ou candidats.",
            NiveauTodo.IMPERATIF,
        )
    ],
    TypeProjet.REUNION_PUBLIQUE: [
        Condition(
            Q(documents__type=TypeDocument.PHOTOGRAPHIE),
            "Des photos de la réunion publique doivent être ajoutées après le déroulement de l'événement.",
            NiveauTodo.AVERTISSEMENT,
        ),
        Condition(
            verifier_transports,
            "La réunion publique doit inclure les dépenses de transport pour chacun des intervenants listés.",
            NiveauTodo.IMPERATIF,
        ),
        Condition(
            verifier_hebergement,
            "La réunion publique doit inclure les dépenses d'hébergement et de restauration pour chacun des intervenants listés.",
            NiveauTodo.IMPERATIF,
        ),
    ],
    TypeProjet.REUNION_PUBLIQUE_ORATEUR: [
        Condition(
            Q(participation__role__in=[Participation.Role.ORATEUR]),
            "La réunion publique doit identifier les orateurs qui s'y sont rendus.",
            NiveauTodo.IMPERATIF,
        )
    ],
    TypeProjet.REUNION_PUBLIQUE_CANDIDAT: [
        Condition(
            Q(participation__role__in=[Participation.Role.CANDIDAT]),
            "La réunion publique doit identifier les candidats et orateurs qui y sont intervenus.",
            NiveauTodo.IMPERATIF,
        )
    ],
}


def todos(projet: Projet):
    todos: List[Tuple[str, List[Tuple[str, NiveauTodo]]]] = []

    generic_todos = []
    if projet.event is None:
        generic_todos.append(
            (
                "Commencez par sélectionner l'événement concerné par ce projet.",
                NiveauTodo.SUGGESTION,
            )
        )

    if generic_todos:
        todos.append(("Informations de base", generic_todos))

    type_todos = []
    for type, conditions in validation_conditions.items():
        if projet.type.startswith(type):
            for cond in conditions:
                if not cond.check(projet):
                    type_todos.append((cond.message_erreur, cond.niveau_erreur))

    if type_todos:
        todos.append(("Contraintes pour ce type de projet", type_todos))

    return todos
