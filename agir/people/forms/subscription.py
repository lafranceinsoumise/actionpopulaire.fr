from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div, Row
from django import forms
from django.utils.translation import ugettext_lazy as _

from agir.lib.data import french_zipcode_to_country_code
from agir.lib.form_components import FormGroup, FullCol
from agir.lib.form_mixins import LocationFormMixin, french_zipcode_validator
from agir.people.models import Person
from agir.people.tasks import (
    send_unsubscribe_email,
    send_confirmation_email,
)


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
            person.newsletters = []
            person.save()
        except Person.DoesNotExist:
            pass
