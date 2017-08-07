from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from django_countries import countries

from .form_components import *

from people.models import Person, PersonEmail
from events.models import Event
from groups.models import SupportGroup


class LocationFormMixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['location_country'].choices = countries


class BaseSubscriptionForm(forms.ModelForm):
    email = forms.EmailField(
        label='Adresse email',
        required=True,
        error_messages={
            'required': _("Vous devez saisir votre adresse email"),
            'unique': _("Cette adresse email est déjà utilisée")
        }
    )

    def clean_email(self):
        """Ensures that the email address is not already in use"""
        email = self.cleaned_data['email']

        if PersonEmail.objects.filter(address=email).exists():
            raise forms.ValidationError(self.fields['email'].error_messages['unique'], code="unique")

        return email

    def _save_m2m(self):
        """Save the email

        _save_m2m is called when the ModelForm instance is saved, whether it is made through
        the form itself using `form.save(commit=True)` or later, using `instance = form.save(commit=False)`
        and calling `instance.save()`later.
        """
        super()._save_m2m()
        PersonEmail.objects.create(address=self.cleaned_data['email'], person=self.instance)

    class Meta:
        abstract = True


class SimpleSubscriptionForm(BaseSubscriptionForm):
    def __init__(self, *args, **kwargs):
        super(SimpleSubscriptionForm, self).__init__(*args, **kwargs)

        self.fields['location_zip'].required = True
        self.fields['location_zip'].help_text = None

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            FormGroup(
                Field("email", placeholder=self.fields['email'].label, css_class='input-lg'),
                css_class="col-sm-12"
            ),
            FormGroup(
                Div(
                    Field("location_zip", placeholder=self.fields['location_zip'].label, css_class='input-lg'),
                    css_class="col-sm-6"
                ),
                Div(
                    Submit('submit', 'Appuyer', css_class="btn-block btn-lg"),
                    css_class="col-sm-6"
                )
            )
        )

    class Meta:
        model = Person
        fields = ('email', 'location_zip')


class OverseasSubscriptionForm(LocationFormMixin, BaseSubscriptionForm):

    def __init__(self, *args, **kwargs):
        super(OverseasSubscriptionForm, self).__init__(*args, **kwargs)

        self.fields['location_country'].required = True
        self.fields['location_address1'].required = True
        self.fields['location_zip'].required = True
        self.fields['location_city'].required = True

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Appuyer'))

        self.helper.layout = Layout(
            Row(
                FullCol('email'),
                Div('location_address1', css_class='col-md-8'),
                Div('location_zip', css_class='col-md-4'),
                HalfCol('location_city'),
                HalfCol('location_country'),
            )
        )

    class Meta:
        model = Person
        fields = (
            'email', 'location_address1', 'location_zip', 'location_city', 'location_country'
        )


class EventForm(LocationFormMixin, forms.ModelForm):
    def __init__(self, calendar, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.calendar = calendar

        self.fields['name'].label = "Nom de l'événement"
        self.fields['name'].help_text = None

        self.fields['location_address1'].label = False
        self.fields['location_address1'].placeholder = _('1ère ligne')

        self.fields['location_address2'].label = False
        self.fields['location_address2'].placeholder = _('2ème ligne')

        self.fields['location_country'].default = 'FR'

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
                    Div(AddressField(), css_class='col-md-12'),
                    Div('location_zip', css_class='col-md-4'),
                    Div('location_city', css_class='col-md-6'),
                    Div('location_country', css_class='col-md-12'),
                ),
                Div('description', css_class='col-md-12'),
            )
        )

    class Meta:
        model = Event
        fields = (
            'name', 'start_time', 'end_time',
            'contact_name', 'contact_email', 'contact_phone',
            'location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip', 'location_country',
            'description'
        )


class SupportGroupForm(LocationFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SupportGroupForm, self).__init__(*args, **kwargs)

        self.fields['location_address1'].label = False
        self.fields['location_address1'].placeholder = _('1ère ligne')

        self.fields['location_address2'].label = False
        self.fields['location_address2'].placeholder = _('2ème ligne')

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Sauvegarder et publier'))

        self.helper.layout = Layout(
            Row(
                Div('name', css_class='col-md-12'),
                Div('start_time', css_class='col-md-6'),
                Div('duration', css_class='col-md-6'),
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
                            "<p><b>Merci d'indiquer une adresse précise avec numéro de rue, sans quoi le groupe"
                            " n'apparaîtra pas sur la carte.</b>"
                            " Si les réunions se déroulent chez vous et que vous ne souhaitez pas rendre cette adresse"
                            " publique, vous pouvez indiquer un endroit à proximité, comme un café, ou votre mairie."),
                        css_class='col-xs-12'
                    ),
                    Div('location_name', css_class='col-md-12'),
                    Div(AddressField(), css_class='col-md-12'),
                    Div('location_zip', css_class='col-md-4'),
                    Div('location_city', css_class='col-md-6'),
                    Div('location_country', css_class='col-md-12'),
                ),
                Div('description', css_class='col-md-12'),
            )
        )

    class Meta:
        model = SupportGroup
        fields = (
            'name',
            'contact_name', 'contact_email', 'contact_phone',
            'location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip', 'location_country',
            'description'
        )
