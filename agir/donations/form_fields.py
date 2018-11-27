from django.conf import settings
from django import forms
from django.forms.widgets import Input
from webpack_loader.utils import get_files


class AmountWidget(Input):
    input_type = "number"
    is_hidden = False

    @property
    def media(self):
        return forms.Media(
            js=[script["url"] for script in get_files("donations/amountWidget", "js")]
        )

    def __init__(self, attrs=None):
        if attrs is None:
            attrs = {}

        attrs.setdefault("step", 1)
        attrs.setdefault("min", settings.DONATION_MINIMUM)
        attrs.setdefault("max", settings.DONATION_MAXIMUM)

        super().__init__(attrs=attrs)
