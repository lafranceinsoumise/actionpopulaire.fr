from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper

from ..form_components import *
from ..form_mixins import LocationFormMixin

from events.models import Event

__all__ = ['EventForm']


class EventForm(LocationFormMixin, forms.ModelForm):
    def __init__(self, calendar, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.calendar = calendar

        self.fields['name'].label = "Nom de l'événement"
        self.fields['name'].help_text = None

        self.fields['location_address1'].placeholder = _('1ère ligne')
        self.fields['location_address1'].required = True

        self.fields['location_address2'].label = False
        self.fields['location_address2'].placeholder = _('2ème ligne')

        for f in ['contact_name', 'contact_email']:
            self.fields[f].required = True

        self.fields['start_time'].widget = DateTimePickerWidget()
        self.fields['end_time'].widget = DateTimePickerWidget()

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sauvegarder et publier'))

        self.helper.layout = Layout(
            Row(
                Div('name', css_class='col-md-12'),
                Div('start_time', css_class='col-md-6'),
                Div('end_time', css_class='col-md-6'),
                Section(
                    _('Informations de contact'),
                    Div('contact_name', css_class='col-md-12'),
                    Div('contact_email', css_class='col-md-6'),
                    Div('contact_phone', css_class='col-md-6'),
                ),
                Section(
                    _('Lieu'),
                    Div(
                        HTML(
                            "<p><b>Merci d'indiquer une adresse précise avec numéro de rue, sans quoi l'événement n'apparaîtra"
                            " pas sur la carte.</b>"
                            " Si les réunions se déroulent chez vous et que vous ne souhaitez pas rendre cette adresse"
                            " publique, vous pouvez indiquer un endroit à proximité, comme un café, ou votre mairie."),
                        css_class='col-xs-12'
                    ),
                    Div('location_name', css_class='col-md-12'),
                    Row(
                        FullCol(
                            Field('location_address1', placeholder=_('1ère ligne')),
                            Field('location_address2', placeholder=_('2ème ligne'))
                        )
                    ),
                    Div('location_zip', css_class='col-md-4'),
                    Div('location_city', css_class='col-md-6'),
                    Div('location_country', css_class='col-md-12'),
                ),
                Div('description', css_class='col-md-12'),
                Div(HTML(
                    "<strong>Cliquez sur sauvegarder et publier pour valider les changements effectués ci-dessous."
                    " Les personnes inscrites à l'événement recevront un message pour les avertir des modifications "
                    " réalisées.</strong>"
                ), css_class='col-xs-12')
            )
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['end_time'] <= cleaned_data['start_time']:
            self.add_error('end_time', _("La fin de l'événément ne peut pas être avant son début."))

    class Meta:
        model = Event
        fields = (
            'name', 'start_time', 'end_time',
            'contact_name', 'contact_email', 'contact_phone',
            'location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
            'location_country',
            'description'
        )
