from django.core.exceptions import ValidationError

from agir.people.person_forms.fields import is_actual_model_field


def validate_custom_fields(custom_fields):
    if not isinstance(custom_fields, list):
        raise ValidationError("La valeur doit être une liste")
    for k, fieldset in enumerate(custom_fields):
        if not (fieldset.get("title")):
            raise ValidationError(f"La section n°{k+1} n'a pas de titre !")

        title = fieldset["title"]

        if "fields" in fieldset:
            if not isinstance(fieldset["fields"], list):
                raise ValidationError(f"La section '{title}' n'a pas de champs !")

            for i, field in enumerate(fieldset["fields"]):
                if field["id"] == "location":
                    initial_field = fieldset["fields"].pop(i)
                    for location_field in [
                        "location_country",
                        "location_state",
                        "location_city",
                        "location_zip",
                        "location_address2",
                        "location_address1",
                    ]:
                        fieldset["fields"].insert(
                            i,
                            {
                                "id": location_field,
                                "person_field": True,
                                "required": False
                                if location_field == "location_address2"
                                else initial_field.get("required", True),
                            },
                        )
                    continue
                if is_actual_model_field(field):
                    continue
                elif not field.get("label") and not field.get("type"):
                    raise ValidationError(
                        f"Section {title}: le champ n°{i+1} n'a ni label ni type"
                    )
                elif not field.get("label"):
                    raise ValidationError(
                        f"Section {title}: le champ n°{i+1} (de type {field['type']}) n'a pas de label"
                    )
                elif not field.get("type"):
                    raise ValidationError(
                        f"Section {title}: le champ {field['label']} n'a pas de type"
                    )
