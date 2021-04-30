from django.db.models import Q

from ..typologies import TypeDepense, TypeDocument

validation_conditions = {
    TypeDepense.FOURNITURE_MARCHANDISES: (
        (
            Q(documents__type=TypeDocument.PHOTOGRAPHIE),
            "Vous devez joindre une photographie de la marchandise pour justifier cette dépense.",
        ),
    ),
    TypeDepense.FRAIS_RECEPTION_HEBERGEMENT: (
        (
            Q(personnes__isnull=False),
            "Vous devez indiquer les personnes concernées par cette dépense.",
        ),
    ),
    TypeDepense.GRAPHISME_MAQUETTAGE: (
        (
            Q(documents__type=TypeDocument.EXEMPLAIRE),
            "Vous devez joindre un exemplaire numérique du graphisme ou du maquettage realisé.",
        )
    ),
}
