from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper

from groups.models import SupportGroup
from ..form_components import *
from ..form_mixins import LocationFormMixin, ContactFormMixin, GeocodingBaseForm

from events.models import Event, OrganizerConfig, Calendar, RSVP
from events.tasks import send_event_creation_notification, send_event_changed_notification
from lib.tasks import geocode_event

__all__ = ['EventForm', 'AddOrganizerForm', 'EventGeocodingForm']


class AgendaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class EventForm(LocationFormMixin, ContactFormMixin, forms.ModelForm):
    CHANGES = {
        'name': "information",
        'start_time': "timing",
        'end_time': "timing",
        'contact_name': "contact",
        'contact_email': "contact",
        'contact_phone': "contact",
        'location_name': "location",
        'location_address1': "location",
        'location_address2': "location",
        'location_city': "location",
        'location_zip': "location",
        'location_country': "location",
        'description': "information"
    }

    def __init__(self, *args, person, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)

        self.person = person

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

        self.fields['as_group'] = forms.ModelChoiceField(
            queryset=SupportGroup.objects.filter(memberships__person=person, memberships__is_manager=True),
            empty_label="Ne pas créer au nom d'un groupe",
            label=_("Créer l'événement au nom d'un groupe d'action"),
            required=False,
        )

        self.fields['name'].label = "Nom de l'événement"
        self.fields['name'].help_text = None

        self.is_creation = self.instance._state.adding

        if not self.is_creation:
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
            self.organizer_config = OrganizerConfig.objects.get(person=self.person, event=self.instance)
            self.fields['as_group'].initial = self.organizer_config.as_group
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
            Row(
                HalfCol('as_group')
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
        res = super().save(commit)

        if commit:
            self.schedule_tasks()

        return res

    def _save_m2m(self):
        if self.is_creation:
            self.organizer_config = OrganizerConfig.objects.create(
                person=self.person,
                event=self.instance,
                as_group=self.cleaned_data['as_group'],
            )
            RSVP.objects.create(
                person=self.person,
                event=self.instance
            )
        elif self.organizer_config.as_group != self.cleaned_data['as_group']:
            self.organizer_config.as_group = self.cleaned_data['as_group']
            self.organizer_config.save()

    def schedule_tasks(self):
        # create set so that values are unique, but turns to list because set are not JSON-serializable
        changes = list({self.CHANGES[field] for field in self.changed_data if field in self.CHANGES})
        address_changed = any(f in self.instance.GEOCODING_FIELDS for f in self.changed_data)

        # if it's a new group creation, send the confirmation notification and geolocate it
        if self.is_creation:
            # membership attribute created by _save_m2m
            send_event_creation_notification.delay(self.organizer_config.pk)
            geocode_event.delay(self.instance.pk)
        else:
            # send changes notification if the notify checkbox was checked
            if changes and self.cleaned_data.get('notify'):
                send_event_changed_notification.delay(self.instance.pk, changes)
            # also geocode again if location has changed
            if address_changed and self.instance.should_relocate_when_address_changed():
                geocode_event.delay(self.instance.pk)

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


class EventGeocodingForm(GeocodingBaseForm):
    geocoding_task = geocode_event
    messages = {
        'use_geocoding': _("La localisation de votre événement sur la carte va être réinitialisée à partir de son adresse."
                           " Patientez quelques minutes pour voir la nouvelle localisation apparaître."),
        'coordinates_updated': _("La localisation de votre événement a été correctement mise à jour. Patientez quelques"
                                 " minutes pour la voir apparaître sur la carte.")
    }

    class Meta:
        model = Event
        fields = ('coordinates',)
