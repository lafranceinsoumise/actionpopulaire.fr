from django.forms import BooleanField, ModelForm


class LegacySubscribedMixin(ModelForm):
    subscribed = BooleanField(
        label="Recevoir les lettres d'information de la France insoumise",
        help_text="Vous recevrez les lettres d'informations de la France insoumise, comme l'actualité hebdomadaire, les"
        " appels à volontaires, les annonces d'émissions ou d'événements...",
        required=False,
    )
