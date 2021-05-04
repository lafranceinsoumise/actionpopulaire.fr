from django.db.models import Q

from .commentaires import nombre_commentaires_a_faire
from ..models import Depense
from ..typologies import TypeDepense, TypeDocument

validation_conditions = {
    TypeDepense.FOURNITURE_MARCHANDISES: (
        (
            Q(documents__type=TypeDocument.PHOTOGRAPHIE),
            "Vous devez joindre une photographie de la marchandise pour justifier cette dépense.",
            "imperatif",
        ),
    ),
    TypeDepense.FRAIS_RECEPTION_HEBERGEMENT: (
        (
            Q(personnes__isnull=False),
            "Les dépenses de réception ou d'hébergement doivent identifier les personnes bénéficiaires de la dépense.",
            "imperatif",
        ),
    ),
    TypeDepense.GRAPHISME_MAQUETTAGE: (
        (
            Q(documents__type=TypeDocument.EXEMPLAIRE),
            "Vous devez joindre un exemplaire numérique du graphisme ou du maquettage realisé.",
            "imperatif",
        )
    ),
}


def todo(depense: Depense):
    todos = []

    if depense.date_depense is None:
        if not depense.documents.filter(Q(type=TypeDocument.DEVIS)).exists():
            todos.append(
                (
                    "Engagement de la dépense",
                    [
                        (
                            "Vous devez joindre le devis pour permettre l'engagement de la dépense.",
                            "imperatif",
                        )
                    ],
                )
            )
        else:
            todos.append(
                (
                    "Engagement de la dépense",
                    [
                        (
                            "La dépense doit avoir été engagé par le responsable du compte.",
                            "imperatif",
                        )
                    ],
                )
            )
    else:
        type_todos = []
        for type in validation_conditions:
            if depense.type.startswith(type):
                for cond, message, niveau in validation_conditions[type]:
                    if not Depense.objects.filter(cond, id=depense.id).exists():
                        type_todos.append((message, niveau))

        if type_todos:
            todos.append(("Lié à ce type de dépense", type_todos))

    coms = nombre_commentaires_a_faire(depense)
    if coms:
        todos.append(
            (
                "Commentaires à traiter",
                [
                    (
                        f"Il y a {coms} commentaire{'s' if coms > 1 else ''} à traiter",
                        "imperatif",
                    ),
                ],
            )
        )

    return todos
