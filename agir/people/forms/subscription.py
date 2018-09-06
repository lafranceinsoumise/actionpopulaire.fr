from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, Row
from django import forms
from django.utils.translation import ugettext_lazy as _

from agir.lib.form_components import FormGroup, FullCol
from agir.lib.form_mixins import LocationFormMixin
from agir.lib.mailtrain import delete_email
from agir.people.models import Person, PersonEmail
from agir.people.tasks import send_unsubscribe_email, send_welcome_mail


class UnsubscribeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Me désabonner'))

    email = forms.EmailField(
        label='Adresse email',
        required=True,
        error_messages={
            'required': _("Vous devez saisir votre adresse email")
        }
    )

    def unsubscribe(self):
        email = self.cleaned_data['email']
        try:
            person = Person.objects.get(email=email)
            send_unsubscribe_email.delay(person.id)
            person.group_notifications = False
            person.event_notifications = False
            person.subscribed = False
            person.save()
        except(Person.DoesNotExist):
            delete_email(email)


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
        send_welcome_mail.delay(self.instance.pk)

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

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('submit', 'Appuyer'))

        self.helper.layout = Layout(
            Row(
                FullCol('email'),
            ),
            Row(
                FullCol(
                    Field('location_address1', placeholder='Ligne 1*'),
                    Field('location_address2', placeholder='Ligne 2'),
                )

            ),
            Row(
                Div('location_zip', css_class='col-md-4'),
                Div('location_city', css_class='col-md-8'),
            ),
            Row(
                FullCol('location_country'),
            )
        )

    class Meta:
        model = Person
        fields = (
            'email', 'location_address1', 'location_address2', 'location_zip', 'location_city', 'location_country'
        )
