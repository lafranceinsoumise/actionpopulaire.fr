import django_countries.data
from data_france.models import Commune

from agir.people.models import Person
from agir.people.person_forms import fields
from agir.people.person_forms.fields import PREDEFINED_CHOICES

uuid = {
    "type": "string",
    "pattern": "^[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$",
    "minLength": 32,
}


choices = {
    "predefined": {"type": "string", "enum": list(PREDEFINED_CHOICES.keys())},
    "values": {"type": "array", "items": {"type": ["string", "number"]}},
    "labels": {
        "type": "array",
        "maxItems": 2,
        "minItems": 2,
        "items": {"type": ["string", "number"]},
    },
    "categories": {
        "type": "array",
        "items": {
            "oneOf": [
                {"type": "string"},
                {
                    "type": "array",
                    "maxItems": 2,
                    "minItems": 2,
                    "items": {"type": ["string", "number"]},
                },
            ]
        },
    },
}

field_commons = {
    "properties": {
        "id": {
            "description": "L'identifiant unique du champ",
            "type": "string",
        },
        "label": {
            "description": "Le libellé du champ",
            "type": "string",
        },
        "person_field": {
            "description": "Le champ doit-il être enregistré sur la personne",
            "type": "boolean",
            "const": True,
        },
        "type": {
            "description": "Le type de champ",
            "type": "string",
            "enum": list(fields.FIELDS.keys()),
        },
        "required": {
            "description": "Le champ est obligatoire",
            "type": "boolean",
        },
        "disabled": {
            "description": "Le champ est en lecture-seule",
            "type": "boolean",
        },
        "initial": {
            "description": "La valeur initiale du champ",
            "type": [
                "number",
                "string",
                "boolean",
                "object",
                "array",
                "null",
            ],
        },
    }
}

field_types = [
    {
        "properties": {
            "type": {
                "const": "short_text",
            },
            "initial": {"type": "string"},
            "min_length": {
                "type": "integer",
            },
            "max_length": {
                "type": "integer",
            },
            "strip": {
                "type": "boolean",
            },
        },
    },
    {
        "properties": {
            "type": {
                "const": "long_text",
            },
            "initial": {"type": "string"},
            "min_length": {"type": "integer"},
            "max_length": {"type": "integer"},
            "strip": {"type": "boolean"},
        },
    },
    {
        "properties": {
            "type": {
                "const": "choice",
            },
            "initial": {"type": ["string", "number"]},
            "default_label": {"type": "string"},
            "empty_value": {"type": "boolean"},
            "choices": {"oneOf": list(choices.values())},
        },
        "required": ["choices"],
    },
    {
        "properties": {
            "type": {
                "const": "radio_choice",
            },
            "initial": {"type": ["string", "number"]},
            "choices": {
                "oneOf": [
                    choices["predefined"],
                    choices["values"],
                    choices["labels"],
                ]
            },
        },
        "required": ["choices"],
    },
    {
        "properties": {
            "type": {
                "const": "autocomplete_choice",
            },
            "initial": {"type": ["string", "number"]},
            "default_label": {"type": "string"},
            "empty_value": {"type": "boolean"},
            "choices": {"oneOf": list(choices.values())},
        },
        "required": ["choices"],
    },
    {
        "properties": {
            "type": {
                "const": "autocomplete_multiple_choice",
            },
            "initial": {"type": ["string", "number"]},
            "max_items": {"type": "integer"},
            "choices": {"oneOf": list(choices.values())},
        },
        "required": ["choices"],
    },
    {
        "properties": {
            "type": {
                "const": "multiple_choice",
            },
            "initial": {"type": ["string", "number"]},
            "choices": {
                "oneOf": [
                    choices["predefined"],
                    choices["values"],
                    choices["labels"],
                ],
            },
        },
        "required": ["choices"],
    },
    {
        "properties": {
            "type": {"const": "email_address"},
            "initial": {"type": "string"},
        }
    },
    {
        "properties": {
            "type": {
                "const": "phone_number",
            },
            "initial": {"type": "string"},
            "region": {"type": "string"},
        }
    },
    {
        "properties": {
            "type": {
                "const": "url",
            },
            "initial": {"type": "string"},
        }
    },
    {
        "properties": {
            "type": {
                "const": "file",
            },
            "max_size": {"type": "integer"},
            "allowed_extensions": {"type": "array", "items": {"type": "string"}},
            "multiple": {"type": "boolean"},
        }
    },
    {
        "properties": {
            "type": {
                "const": "boolean",
            },
            "initial": {"type": "boolean"},
        }
    },
    {
        "properties": {
            "type": {"const": "integer"},
            "initial": {"type": "integer"},
            "min_value": {"type": "integer"},
            "max_value": {"type": "integer"},
        }
    },
    {
        "properties": {
            "type": {"const": "decimal"},
            "initial": {"type": "number"},
            "min_value": {"type": "number"},
            "max_value": {"type": "number"},
            "max_digits": {"type": "integer"},
            "decimal_places": {"type": "integer"},
        }
    },
    {
        "properties": {
            "type": {"const": "datetime"},
            "initial": {"type": "string"},
        }
    },
    {
        "properties": {
            "type": {"const": "date"},
            "initial": {"type": "string"},
            "min_value": {"type": "string"},
            "max_value": {"type": "string"},
        }
    },
    {
        "properties": {
            "type": {"const": "dates"},
            "initial": {"type": "string"},
            "min_value": {"type": "string"},
            "max_value": {"type": "string"},
            "min_length": {"type": "integer"},
            "max_length": {"type": "integer"},
            "min_delta": {"type": "integer"},
            "max_delta": {"type": "integer"},
        }
    },
    {
        "properties": {
            "type": {"const": "datetimes"},
            "initial": {"type": "string"},
            "min_value": {"type": "string"},
            "max_value": {"type": "string"},
            "min_length": {"type": "integer"},
            "max_length": {"type": "integer"},
            "min_delta": {"type": "integer"},
            "max_delta": {"type": "integer"},
        }
    },
    {
        "properties": {
            "type": {"const": "person"},
            "initial": uuid,
            "allow_self": {"type": "boolean"},
            "allow_inactive": {"type": "boolean"},
        }
    },
    {
        "properties": {
            "type": {"const": "iban"},
            "initial": {"type": "string"},
            "allowed_countries": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(django_countries.data.COUNTRIES.keys()),
                },
            },
        }
    },
    {
        "properties": {
            "type": {"const": "commune"},
            "initial": {"type": "integer"},
            "types": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(Commune.TypeCommune.values),
                },
            },
        }
    },
    {
        "properties": {
            "type": {"enum": ["group", "multiple_groups"]},
            "initial": uuid,
            "choices": {
                "oneOf": [
                    {
                        "type": "string",
                        "enum": [
                            "animateur",
                            "animatrice",
                            "animator",
                            "referent",
                            "manager",
                            "gestionnaire",
                            "membre",
                            "member",
                        ],
                    },
                    {
                        "type": "array",
                        "items": uuid,
                    },
                ]
            },
        },
        "required": ["choices"],
    },
    {
        "properties": {
            "type": {"const": "newsletters"},
            "initial": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [n[0] for n in Person.NEWSLETTERS_CHOICES],
                },
            },
            "choices": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [n[0] for n in Person.NEWSLETTERS_CHOICES],
                },
            },
        },
        "required": ["choices"],
    },
    {
        "properties": {
            "type": {"const": "event_theme"},
            "initial": uuid,
            "event_theme_type": {"type": ["string", "number"]},
        },
    },
    {
        "properties": {
            "type": {"const": "person_tag"},
            "initial": uuid,
            "choices": {"type": "array", "items": {"type": ["string", "number"]}},
            "multiple": {"type": "boolean"},
        },
        "required": ["choices"],
    },
]

field = {
    "type": "object",
    "allOf": [field_commons, {"oneOf": field_types}],
}

schema = {
    "title": "Person Form",
    "description": "A custom person form definition",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"description": "Le titre du groupe de champ", "type": "string"},
            "intro_html": {
                "description": "Texte introductif au format HTML à afficher sous le titre",
                "type": "string",
            },
            "fields": {
                "description": "La liste des champ",
                "type": "array",
                "minItems": 1,
                "items": field,
            },
        },
        "required": ["title", "fields"],
    },
    "minItems": 1,
}
