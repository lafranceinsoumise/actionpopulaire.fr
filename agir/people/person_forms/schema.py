from agir.people.person_forms import fields

schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"description": "Le titre du groupe de champs", "type": "string"},
            "intro_html": {
                "description": "Texte introductif au format HTML à afficher sous le titre",
                "type": "string",
            },
            "fields": {
                "description": "La liste des champs",
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "description": "L'identifiant court du champ",
                            "type": "string",
                        },
                        "person_field": {
                            "description": "Le champ doit-il être enregistré sur la personne",
                            "type": "boolean",
                            "const": True,
                        },
                        "type": {
                            "description": "Le type du champ",
                            "type": "string",
                            "enum": list(fields.FIELDS.keys()),
                        },
                        "choices": {
                            "description": "La liste des choix",
                            "anyOf": [
                                {
                                    "type": "array",
                                    "items": {
                                        "anyOf": [
                                            {
                                                "type": "array",
                                                "maxItems": 2,
                                                "minItems": 2,
                                                "items": {"type": "string"},
                                            },
                                            {"type": "string"},
                                        ]
                                    },
                                },
                                {"type": "string"},
                                {"type": "number"},
                            ],
                        },
                    },
                    "required": ["id"],
                },
            },
        },
        "required": ["title", "fields"],
    },
    "minItems": 1,
}
