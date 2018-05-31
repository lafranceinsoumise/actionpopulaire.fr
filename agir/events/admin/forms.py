from django.utils.translation import ugettext_lazy as _
from django import forms
from ajax_select.fields import AutoCompleteSelectField

from ...lib.forms import CoordinatesFormMixin
from ...lib.form_fields import AdminRichEditorWidget

from .. import models


class EventAdminForm(CoordinatesFormMixin, forms.ModelForm):
    calendars = forms.ModelMultipleChoiceField(
        queryset=models.Calendar.objects.all(),
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
