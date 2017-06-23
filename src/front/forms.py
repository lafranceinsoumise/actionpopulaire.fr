from django import forms
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field, HTML
from django_countries.fields import LazyTypedChoiceField
from django_countries import countries

from people.models import Person


class Row(Div):
    css_class = "row"


class FormGroup(Div):
    css_class = "form-group"


class SimpleSubscriptionForm(forms.ModelForm):
    email = forms.EmailField(
        label=_("Adresse email"),
        required=True,
        error_messages={
            'unique': _("Cette adresse email est déjà utilisée.")
        }
    )

    location_zip = forms.CharField(
        label=_("Code postal"),
        required=True,
        max_length=5, min_length=5,
    )

    def __init__(self, *args, **kwargs):
        super(SimpleSubscriptionForm, self).__init__(*args, **kwargs)
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


class OverseasSubscriptionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OverseasSubscriptionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Appuyer'))

        self.helper.layout = Layout(
            Div(
                Div('email', css_class='col-md-12'),
                Div('location_address1', css_class='col-md-8'),
                Div('location_zip', css_class='col-md-4'),
                Div('location_city', css_class='col-md-6'),
                Div('location_country', css_class='col-md-6'),
                css_class='row'
            )
        )

    email = forms.EmailField(
        label=_('Email'),
        required=True
    )

    location_address1 = forms.CharField(
        label=_('Adresse'),
        required=True,
        max_length=200
    )

    location_zip = forms.CharField(
        label=_("Code postal"),
        required=True,
        max_length=20, min_length=1,
    )

    location_city = forms.CharField(
        label=_('Ville'),
        required=True,
        max_length=200
    )

    location_country = LazyTypedChoiceField(
        label=_("Pays"),
        required=True,
        choices=countries,
    )

    class Meta:
        model = Person
        fields = (
            'email', 'location_address1', 'location_zip', 'location_city', 'location_country'
        )
