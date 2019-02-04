import json
import uuid
from django import forms
from django.contrib.postgres.forms import JSONField
from django.contrib.postgres.forms.jsonb import InvalidJSONInput
from django.core.exceptions import ValidationError
from django.forms.widgets import Input
from django.utils.translation import ugettext_lazy as _
from webpack_loader.utils import get_files


class MandatesWidget(Input):
    input_type = "hidden"
    is_hidden = False

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}
        attrs["data-mandates"] = "Y"
        super().__init__(attrs=attrs)

    @property
    def media(self):
        return forms.Media(
            js=[script["url"] for script in get_files("people/mandatesField", "js")]
        )


class MandatesField(JSONField):
    default_error_messages = {
        "invalid": _("La valeur de '%(value)s' est mal formatée.")
    }
    widget = MandatesWidget

    def validate(self, value):
        super().validate(value)

        if not isinstance(value, list):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

    def bound_data(self, data, initial):
        if self.disabled:
            return initial
        if data is None:
            return []
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return InvalidJSONInput(data)
