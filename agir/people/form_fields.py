from django import forms
from django.forms.widgets import Input
from django.contrib.postgres.forms import JSONField
from django.utils.translation import ugettext_lazy as _
from webpack_loader.utils import get_files


class MandatesWidget(Input):
    input_type = "hidden"
    is_hidden = False

    @property
    def media(self):
        return forms.Media(
            js=[script["url"] for script in get_files("people/mandatesField", "js")]
        )


class MandatesField(JSONField):
    default_error_messages = {"invalid": _("La valeur de '%(value)' est mal formatée.")}
    widget = MandatesWidget
