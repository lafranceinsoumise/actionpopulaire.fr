from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper

from ..form_components import *
from ..form_mixins import LocationFormMixin, ContactFormMixin

from events.models import Event, OrganizerConfig, Calendar

__all__ = ['EventForm', 'AddOrganizerForm']


class AgendaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.title


class EventForm(LocationFormMixin, ContactFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        calendar_field = []

        description_field = [
            'description'
        ]

        # do not allow random organizers to modify HTML
        if self.instance.allow_html:
            del self.fields['description']
            description_field = []

        if not hasattr(self.instance, 'calendar') or self.instance.calendar.user_contributed:
            self.fields['calendar'] = AgendaChoiceField(
                Calendar.objects.filter(user_contributed=True),
                empty_label=None,
                label=_("Type d'événement"),
                required=True,
                widget=forms.RadioSelect()
            )

            calendar_field = [Row(FullCol('calendar'))]

        self.fields['name'].label = "Nom de l'événement"
        self.fields['name'].help_text = None

        self.fields['start_time'].widget = DateTimePickerWidget()
        self.fields['end_time'].widget = DateTimePickerWidget()

        is_creation = self.instance._state.adding

        if not is_creation:
            self.fields['notify'] = forms.BooleanField(
                required=False,
                initial=False,
                label=_("Signalez ces changements aux participants à l'événement"),
                help_text=_("Un email sera envoyé à la validation de ce formulaire. Merci de ne pas abuser de cette"
                            " fonctionnalité.")
            )
            notify_field = [Row(
                FullCol('notify')
            )]
        else:
            notify_field = []

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sauvegarder et publier'))

        self.helper.layout = Layout(
            Row(
                FullCol('name'),
            ),
            *calendar_field,
            Row(
                HalfCol('start_time'),
                HalfCol('end_time'),
            ),
            Section(
                _('Informations de contact'),
                Row(
                    FullCol('contact_name'),
                ),
                Row(
                    HalfCol('contact_email'),
                    HalfCol('contact_phone', 'contact_hide_phone'),
                ),
            ),
            Section(
                _('Lieu'),
                Row(
                    FullCol(
                        HTML(
                            "<p><b>Merci d'indiquer une adresse précise avec numéro de rue, sans quoi l'événement n'apparaîtra"
                            " pas sur la carte.</b>"
                            " Si les réunions se déroulent chez vous et que vous ne souhaitez pas rendre cette adresse"
                            " publique, vous pouvez indiquer un endroit à proximité, comme un café, ou votre mairie.",
                        ),
                    )
                ),
                Row(
                    FullCol('location_name', css_class='col-md-12'),
                ),
                Row(
                    FullCol(
                        Field('location_address1', placeholder=_('1ère ligne')),
                        Field('location_address2', placeholder=_('2ème ligne'))
                    )
                ),
                Row(
                    Div('location_zip', css_class='col-md-4'),
                    Div('location_city', css_class='col-md-8'),
                ),
                Row(
                    Div('location_country', css_class='col-md-12'),
                ),
            ),
            *description_field,
            *notify_field,
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['end_time'] <= cleaned_data['start_time']:
            self.add_error('end_time', _("La fin de l'événément ne peut pas être avant son début."))

    def save(self, commit=True):
        return super().save(commit)

    class Meta:
        model = Event
        fields = (
            'name', 'start_time', 'end_time', 'calendar',
            'contact_name', 'contact_email', 'contact_phone', 'contact_hide_phone',
            'location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
            'location_country',
            'description'
        )


class RSVPChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.person)


class AddOrganizerForm(forms.Form):
    form = forms.CharField(initial="add_organizer_form", widget=forms.HiddenInput())

    def __init__(self, event, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event

        self.fields['organizer'] = RSVPChoiceField(
            queryset=event.rsvps.exclude(person__organized_events=event), label=False
        )

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', _('Ajouter comme co-organisateur')))

    def save(self, commit=True):
        rsvp = self.cleaned_data['organizer']

        organizer_config = OrganizerConfig(
            event=rsvp.event,
            person=rsvp.person
        )

        if commit:
            organizer_config.save()

        return organizer_config