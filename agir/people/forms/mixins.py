from django.forms import BooleanField, ModelForm

from agir.people.models import Person


class LegacySubscribedMixin(ModelForm):
    subscribed_lfi = BooleanField(
        label="Recevoir les lettres d'information de la France insoumise",
        help_text="Vous recevrez les lettres d'informations de la France insoumise, comme l'actualité hebdomadaire, les"
        " appels à volontaires, les annonces d'émissions ou d'événements...",
        required=False,
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(
            *args,
            instance=instance,
            **kwargs,
        )

        self.fields["subscribed_lfi"].initial = (
            instance is not None and Person.NEWSLETTER_LFI in instance.newsletters
        )

    def save(self, commit=True):
        if "subscribed_lfi" not in self.fields:
            return super().save(commit)
        subscribed_lfi = self.cleaned_data.get("subscribed_lfi", False)
        if subscribed_lfi and Person.NEWSLETTER_LFI not in self.instance.newsletters:
            self.instance.newsletters.append(Person.NEWSLETTER_LFI)
        elif not subscribed_lfi and Person.NEWSLETTER_LFI in self.instance.newsletters:
            self.instance.newsletters.remove(Person.NEWSLETTER_LFI)
        return super().save(commit)
