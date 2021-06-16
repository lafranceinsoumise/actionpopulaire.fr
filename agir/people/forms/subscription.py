from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import ugettext_lazy as _

from agir.people.models import Person
from agir.notifications.models import Subscription
from agir.activity.models import Activity
from agir.people.tasks import send_unsubscribe_email


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
            person.newsletters = []
            for s in Subscription.objects.filter(
                type=Activity.SUBSCRIPTION_EMAIL, person=person
            ):
                s.delete()
            person.subscribed = False
            person.save()
        except Person.DoesNotExist:
            pass
