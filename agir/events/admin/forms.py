from django import forms
from django.utils.translation import ugettext_lazy as _
from ajax_select.fields import AutoCompleteSelectField

from ...lib.forms import CoordinatesFormMixin
from ...lib.form_fields import AdminRichEditorWidget

from .. import models


class CalendarIterator:
    """Simple iterator

    We cannot use a generator expression, because Django often needs to copy widgets (and thus
    choices iterators), and use pickling for that: however, generator expressions are not
    picklable.

    """
    def __init__(self, field):
        self.field = field

    def __iter__(self):
        return ((c.pk, self.field.label_from_instance(c)) for c in self.field.get_queryset())


class CalendarField(forms.Field):
    widget = forms.SelectMultiple
    default_error_messages = {
        'invalid_choice': "Choix invalide",
        'invalid_list': 'Devrait être une liste'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widget.choices = CalendarIterator(self)

    def to_python(self, value):
        if value in self.empty_values:
            return []

        try:
            value = frozenset(str(c) for c in value)
        except TypeError:
            raise forms.ValidationError(self.error_messages['invalid_list'], 'invalid_list')

        queryset = self.get_queryset()
        ids = {str(c.pk) for c in queryset}
        for pk in value:
            if str(pk) not in ids:
                raise forms.ValidationError(self.error_messages['invalid_choice'], params={'value': value})

        return [c for c in queryset if str(c.pk) in value]

    def prepare_value(self, value):
        return [getattr(c, 'pk', c) for c in value]

    def get_queryset(self):
            return models.Calendar.objects.raw('''
                        WITH RECURSIVE calendars AS (
                            SELECT id, name, 0 AS depth, slug::text AS path
                            FROM events_calendar
                            WHERE parent_id IS NULL
                          UNION ALL 
                            SELECT c.id, c.name, p.depth + 1 AS depth, CONCAT(p.path, ':', c.slug) AS path
                            FROM events_calendar AS c
                            JOIN calendars AS p
                            ON parent_id = p.id
                        )
                        SELECT id, name, depth
                        FROM calendars
                        ORDER BY path;
                    ''')

    def label_from_instance(self, obj):
        return (((obj.depth -1 ) * "\u2003" + "\u2ba1 ") if obj.depth else "") + obj.name


class EventAdminForm(CoordinatesFormMixin, forms.ModelForm):
    calendars = CalendarField(
        required=False,
        label='Agendas',
        help_text=_('Maintenez appuyé « Ctrl », ou « Commande (touche pomme) » sur un Mac, pour en sélectionner plusieurs.')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['calendars'].initial = self.instance.calendars.all()

    def _save_m2m(self):
        super()._save_m2m()

        current_calendars = set(c.pk for c in self.instance.calendars.all())
        new_calendars = set(c.pk for c in self.cleaned_data['calendars'])

        # delete items for removed calendars
        models.CalendarItem.objects.filter(
            event=self.instance, calendar_id__in=current_calendars - new_calendars
        ).delete()

        # add items for added calendars
        models.CalendarItem.objects.bulk_create(
            models.CalendarItem(event=self.instance, calendar_id=c) for c in new_calendars - current_calendars
        )

    class Meta:
        exclude = (
            'id', 'organizers', 'attendees'
        )
        widgets = {
            'description': AdminRichEditorWidget(),
            'report_content': AdminRichEditorWidget(),
        }


class AddOrganizerForm(forms.Form):
    person = AutoCompleteSelectField(
        "people",
        required=True,
        label=_("Personne à ajouter"),
        help_text=""
    )

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

    def clean_person(self):
        person = self.cleaned_data['person']
        if models.OrganizerConfig.objects.filter(person=person, event=self.event).exists():
            raise forms.ValidationError(_("Cette personne organise déjà à cet événement"))

        return person

    def save(self):
        return models.OrganizerConfig.objects.create(person=self.cleaned_data['person'], event=self.event)
