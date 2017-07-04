from crispy_forms.layout import Layout, Submit, Div, Field, MultiField, HTML

from django.forms.widgets import DateTimeBaseInput
from django.utils import formats


class Row(Div):
    css_class = "row"


class FullCol(Div):
    css_class = "col-xs-12"


class HalfCol(Div):
    css_class = "col-xs-12 col-md-6"


class FormGroup(Div):
    css_class = "form-group"


def Section(title, *args):
    return Div(
        HTML(f'<h4 class="padtopmore padbottom col-xs-12">{title}</h4>'),
        *args
    )


def AddressField():
    return Div(
        HTML('<label for="id_location_address1">Adresse</label>'),
        Field('location_address1', placeholder='1ère ligne'),
        Field('location_address2', placeholder='2ème ligne (optionnel)'),
    )


class DateTimePickerWidget(DateTimeBaseInput):
    template_name = 'front/fields/date_time_picker.html'

    def format_value(self, value):
        return formats.localize_input(value, "%d/%m/%Y %H:%M")
