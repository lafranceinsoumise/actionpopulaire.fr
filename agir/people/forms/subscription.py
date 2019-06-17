from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, Row
from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from agir.lib.data import french_zipcode_to_country_code
from agir.lib.form_components import FormGroup, FullCol
from agir.lib.form_mixins import LocationFormMixin
from agir.lib.mailtrain import delete_email
from agir.people.models import Person
from agir.people.tasks import send_unsubscribe_email, send_confirmation_email


class AnonymousUnsubscribeForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Me désabonner"))

    email = forms.EmailField(
        label="Adresse email",
        required=True,
        error_messages={"required": _("Vous devez saisir votre adresse email")},
    )

    def unsubscribe(self):
        email = self.cleaned_data["email"]
        try:
            person = Person.objects.get(email=email)
            send_unsubscribe_email.delay(person.id)
            person.group_notifications = False
            person.event_notifications = False
            person.subscribed = False
            person.save()
        except (Person.DoesNotExist):
            delete_email(email)


class BaseSubscriptionForm(forms.Form):
    email = forms.EmailField(
        label="Adresse email",
        required=True,
        error_messages={
            "required": _("Vous devez saisir votre adresse email"),
            "unique": _("Cette adresse email est déjà utilisée"),
        },
    )

    def send_confirmation_email(self):
        """Sends the confirmation mail
        """
        send_confirmation_email.delay(**self.cleaned_data)


class SimpleSubscriptionForm(BaseSubscriptionForm):
    location_zip = forms.CharField(
        label="Code postal",
        validators=[
            RegexValidator(r"[0-9]{5}", message="Entrez un code postal français")
        ],
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(SimpleSubscriptionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            FormGroup(
                Field(
                    "email",
                    placeholder=self.fields["email"].label,
                    css_class="input-lg",
                ),
                css_class="col-sm-12",
            ),
            FormGroup(
                Div(
                    Field(
                        "location_zip",
                        placeholder=self.fields["location_zip"].label,
                        css_class="input-lg",
                    ),
                    css_class="col-sm-6",
                ),
                Div(
                    Submit("submit", "Appuyer", css_class="btn-block btn-lg"),
                    css_class="col-sm-6",
                ),
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        if "location_zip" in cleaned_data:
            cleaned_data["location_country"] = french_zipcode_to_country_code(
                cleaned_data["location_zip"]
            )

        return cleaned_data


class OverseasSubscriptionForm(LocationFormMixin, BaseSubscriptionForm):
    # make sure the location name field is not shown
    location_name = None

    def __init__(self, *args, **kwargs):
        super(OverseasSubscriptionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "POST"
        self.helper.add_input(Submit("submit", "Appuyer"))

        self.helper.layout = Layout(
            Row(FullCol("email")),
            Row(
                FullCol(
                    Field("location_address1", placeholder="Ligne 1*"),
                    Field("location_address2", placeholder="Ligne 2"),
                )
            ),
            Row(
                Div("location_zip", css_class="col-md-4"),
                Div("location_city", css_class="col-md-8"),
            ),
            Row(FullCol("location_country")),
        )
