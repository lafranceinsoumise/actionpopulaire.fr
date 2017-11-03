from crispy_forms.layout import Layout, Submit, Div, Field, MultiField, HTML, Row

from django.forms.widgets import DateTimeBaseInput, Textarea
from django.utils import formats


class FullCol(Div):
    css_class = "col-xs-12"


class HalfCol(Div):
    css_class = "col-xs-12 col-md-6"


class FormGroup(Div):
    css_class = "form-group"


def Section(title, *args):
    return Div(
        HTML(f'<h4 class="padtopmore padbottom">{title}</h4>'),
        *args
    )


class DateTimePickerWidget(DateTimeBaseInput):
    template_name = 'front/fields/date_time_picker.html'

    def format_value(self, value):
        return formats.localize_input(value, "%d/%m/%Y %H:%M")

    class Media:
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.37/css/bootstrap-datetimepicker.min.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.18.1/moment.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.18.1/locale/fr.js',
            'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datetimepicker/4.17.37/js/bootstrap-datetimepicker.min.js'
        )


class MarkdownDescriptionWidget(Textarea):
    template_name = 'front/fields/markdown_description.html'

    class Media:
        js = (
            'js/markdownEditor.js',
        )
