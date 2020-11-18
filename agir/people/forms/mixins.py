from django.forms import BooleanField, ModelForm

from agir.people.models import Person


class LegacySubscribedMixin(ModelForm):
    subscribed_lfi = BooleanField(
        label="Recevoir les lettres d'information",
        help_text="Vous recevrez les lettres de la France insoumise, notamment : les lettres d'information, les"
        " appels à volontaires, les annonces d'émissions ou d'événements...",
        required=False,
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(
            *args, instance=instance, **kwargs,
        )

        self.fields["subscribed_lfi"].initial = (
            instance is not None and Person.NEWSLETTER_LFI in instance.newsletters
        )

    def save(self, commit=True):
        subscribed_lfi = self.cleaned_data.get("subscribed_lfi", False)
        if subscribed_lfi and Person.NEWSLETTER_LFI not in self.instance.newsletters:
            self.instance.newsletters.append(Person.NEWSLETTER_LFI)
        elif not subscribed_lfi and Person.NEWSLETTER_LFI in self.instance.newsletters:
            self.instance.newsletters.remove(Person.NEWSLETTER_LFI)
        return super().save(commit)
