from agir.events.models import EventSubtype

QUESTIONS = [
    {
        "id": "salle",
        "question": "L'événement aura-t-il lieu en intérieur (autre qu'un domicile personnel) ?",
        "helpText": "Répondez oui si l'événement sera organisé dans une salle, dans un bar ou dans un autre lieu privé.",
        "type": [EventSubtype.TYPE_PUBLIC_MEETING, EventSubtype.TYPE_OTHER_EVENTS],
    },
    {
        "id": "installation-technique",
        "question": "Cet événement nécessite-t-il une installation technique (sono, barnum, praticable...) ?",
        "type": [
            EventSubtype.TYPE_PUBLIC_MEETING,
            EventSubtype.TYPE_PUBLIC_ACTION,
            EventSubtype.TYPE_OTHER_EVENTS,
        ],
    },
    {
        "id": "candidat",
        "question": "Votre événement fait-il intervenir un candidat aux élections européennes ?",
        "type": [
            EventSubtype.TYPE_PUBLIC_ACTION,
            EventSubtype.TYPE_PUBLIC_MEETING,
            EventSubtype.TYPE_OTHER_EVENTS,
        ],
    },
    {
        "id": "materiel-campagne",
        "question": "Utiliserez-vous du matériel siglé campagne européenne pendant votre événement ?",
        "type": [
            EventSubtype.TYPE_PUBLIC_ACTION,
            EventSubtype.TYPE_PUBLIC_MEETING,
            EventSubtype.TYPE_OTHER_EVENTS,
        ],
        "notWhen": "candidat",
    },
    {
        "id": "impressions-propres-moyens",
        "question": "Imprimerez-vous ce matériel grâce à une imprimante personnelle ?",
        "helpText": "Vous ne pouvez pas payer vous-mêmes une impression chez un imprimeur. Toutes les dépenses"
        " électorales doivent être réalisées par l'association de financement de la campagne européenne.",
        "type": [
            EventSubtype.TYPE_PUBLIC_MEETING,
            EventSubtype.TYPE_PUBLIC_ACTION,
            EventSubtype.TYPE_OTHER_EVENTS,
        ],
        "when": "materiel-campagne",
    },
    {
        "id": "frais",
        "question": "Allez-vous engager des frais auprès de commerçants ou entreprises ?",
        "helpText": "Si vous souhaitez engager des frais, il vaut le déclarer dès maintenant afin que la dépense soit"
        "autorisée par la campagne.",
    },
]
