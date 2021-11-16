"""Contient des définitions obsolètes utilisées pendant la campagne des
européennes 2019.

Ces définitions ne sont gardées que pour des raisons documentaires.
"""

from agir.events.models import EventSubtype

QUESTION_SALLE = "salle"
QUESTION_INSTALLATION_TECHNIQUE = "installation_technique"
QUESTION_CANDIDAT = "candidat"
QUESTION_MATERIEL_CAMPAGNE = "materiel_campagne"
QUESTION_IMPRESSION = "impressions_propres_moyens"
QUESTION_FRAIS = "frais"

LEGACY_QUESTIONS = [
    {
        "id": QUESTION_CANDIDAT,
        "question": "Votre événement fait-il intervenir un candidat aux élections européennes ?",
        "type": [
            EventSubtype.TYPE_PUBLIC_ACTION,
            EventSubtype.TYPE_PUBLIC_MEETING,
            EventSubtype.TYPE_OTHER_EVENTS,
        ],
    },
    {
        "id": QUESTION_MATERIEL_CAMPAGNE,
        "question": "Utiliserez-vous du matériel siglé campagne européenne pendant votre événement ?",
        "type": [
            EventSubtype.TYPE_PUBLIC_ACTION,
            EventSubtype.TYPE_PUBLIC_MEETING,
            EventSubtype.TYPE_OTHER_EVENTS,
        ],
        "notWhen": "candidat",
    },
    {
        "id": QUESTION_IMPRESSION,
        "question": "Imprimerez-vous ce matériel grâce à une imprimante personnelle ?",
        "helpText": "Vous ne pouvez pas payer vous-mêmes une impression chez un imprimeur. Toutes les dépenses"
        " électorales doivent être réalisées par l'association de financement de la campagne européenne.",
        "type": [
            EventSubtype.TYPE_PUBLIC_MEETING,
            EventSubtype.TYPE_PUBLIC_ACTION,
            EventSubtype.TYPE_OTHER_EVENTS,
        ],
        "when": "materiel_campagne",
    },
]

ASKED_QUESTIONS = [
    {
        "id": QUESTION_SALLE,
        "question": "L'événement aura-t-il lieu en intérieur (autre qu'un domicile personnel) ?",
        "helpText": "Répondez oui si l'événement sera organisé dans une salle, dans un bar ou dans un autre lieu privé.",
        "type": [EventSubtype.TYPE_PUBLIC_MEETING, EventSubtype.TYPE_OTHER_EVENTS],
    },
    {
        "id": QUESTION_INSTALLATION_TECHNIQUE,
        "question": "Cet événement nécessite-t-il une installation technique (sono, barnum, praticable...) ?",
        "type": [
            EventSubtype.TYPE_PUBLIC_MEETING,
            EventSubtype.TYPE_PUBLIC_ACTION,
            EventSubtype.TYPE_OTHER_EVENTS,
        ],
    },
    {
        "id": QUESTION_FRAIS,
        "question": "Souhaitez-vous engager des frais auprès de commerçants ou entreprises ?",
        "helpText": "Si vous souhaitez engager des frais, il faut le déclarer dès maintenant afin que la dépense soit "
        "préalablement autorisée par l'association de financement.",
    },
]

QUESTIONS_DICT = {
    question.get("id"): question for question in LEGACY_QUESTIONS + ASKED_QUESTIONS
}
