from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper

from ..form_components import *
from ..form_mixins import LocationFormMixin, ContactFormMixin

from events.models import Event

__all__ = ['EventForm']


class EventForm(LocationFormMixin, ContactFormMixin, forms.ModelForm):
    def __init__(self, calendar=None, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.calendar = calendar

        self.fields['name'].label = "Nom de l'événement"
        self.fields['name'].help_text = None

        self.fields['start_time'].widget = DateTimePickerWidget()
        self.fields['end_time'].widget = DateTimePickerWidget()

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sauvegarder et publier'))

        self.helper.layout = Layout(
            Row(
                FullCol('name'),
            ),
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
            Row(
                FullCol('description'),
            ),
            Row(
                FullCol(
                    HTML(
                        "<strong>Cliquez sur sauvegarder et publier pour valider les changements effectués ci-dessous."
                        " Les personnes inscrites à l'événement recevront un message pour les avertir des modifications "
                        " réalisées.</strong>"
                    )
                )
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['end_time'] <= cleaned_data['start_time']:
            self.add_error('end_time', _("La fin de l'événément ne peut pas être avant son début."))

    def save(self, commit=True):
        if self.calendar:
            self.instance.calendar = self.calendar
        return super().save(commit)

    class Meta:
        model = Event
        fields = (
            'name', 'start_time', 'end_time',
            'contact_name', 'contact_email', 'contact_phone', 'contact_hide_phone',
            'location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
            'location_country',
            'description'
        )
