from django.forms.widgets import Textarea, DateTimeBaseInput
from django.utils import formats


class DateTimePickerWidget(DateTimeBaseInput):
    template_name = 'custom_fields/date_time_picker.html'

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


class RichEditorWidget(Textarea):
    template_name = 'custom_fields/rich_editor.html'
    admin = False

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['admin'] = self.admin
        return context

    class Media:
        js = (
            'components/richEditor.js',
        )

class AdminRichEditorWidget(RichEditorWidget):
    admin = True
