import urllib.parse
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.lib.http import add_query_params_to_url
from agir.people.models import Person


def make_subscription_token(email, **kwargs):
    return subscription_confirmation_token_generator.make_token(email=email, **kwargs)


@dataclass
class SubscriptionMessageInfo:
    code: str
    subject: str
    from_email: str = settings.EMAIL_FROM


SUBSCRIPTION_TYPE_LFI = "LFI"
SUBSCRIPTION_TYPE_NSP = "NSP"
SUBSCRIPTION_TYPE_EXTERNAL = "EXT"
SUBSCRIPTION_TYPE_CHOICES = (
    (SUBSCRIPTION_TYPE_LFI, "LFI",),
    (SUBSCRIPTION_TYPE_NSP, "NSP",),
    (SUBSCRIPTION_TYPE_EXTERNAL, "Externe"),
)
SUBSCRIPTION_FIELD = {
    SUBSCRIPTION_TYPE_LFI: "is_insoumise",
    SUBSCRIPTION_TYPE_NSP: "is_2022",
}

SUBSCRIPTIONS_EMAILS = {
    SUBSCRIPTION_TYPE_LFI: {
        "confirmation": SubscriptionMessageInfo(
            "SUBSCRIPTION_CONFIRMATION_LFI_MESSAGE",
            "Plus qu'un clic pour vous inscrire",
        ),
        "already_subscribed": SubscriptionMessageInfo(
            "ALREADY_SUBSCRIBED_LFI_MESSAGE", "Vous êtes déjà inscrits !",
        ),
        "welcome": SubscriptionMessageInfo(
            "WELCOME_LFI_MESSAGE", "Bienvenue sur la plateforme de la France insoumise"
        ),
    },
    SUBSCRIPTION_TYPE_NSP: {
        "confirmation": SubscriptionMessageInfo(
            "SUBSCRIPTION_CONFIRMATION_NSP_MESSAGE",
            "Confirmez votre e-mail pour valider votre signature !",
            "nepasrepondre@noussommespour.fr",
        )
    },
    SUBSCRIPTION_TYPE_EXTERNAL: {},
}
SUBSCRIPTION_NEWSLETTERS = {
    SUBSCRIPTION_TYPE_LFI: {Person.NEWSLETTER_LFI},
    SUBSCRIPTION_TYPE_NSP: {Person.NEWSLETTER_2022},
    SUBSCRIPTION_TYPE_EXTERNAL: set(),
}


def save_subscription_information(person, type, data):
    person_fields = set(f.name for f in Person._meta.get_fields())

    # mise à jour des différents champs
    for f in person_fields.intersection(data):
        # On ne remplace que les champs vides de la personne
        setattr(person, f, getattr(person, f) or data[f])

    person.newsletters = list(SUBSCRIPTION_NEWSLETTERS[type].union(person.newsletters))

    if not getattr(person, SUBSCRIPTION_FIELD[type]):
        setattr(person, SUBSCRIPTION_FIELD[type], True)
        subscriptions = person.meta.setdefault("subscriptions", {})
        subscriptions[SUBSCRIPTION_FIELD[type]] = {
            "date": timezone.now().strftime("%Y/%m/%d")
        }
        if data.get("referer") and Person.objects.filter(pk=data["referer"]).exists():
            subscriptions[SUBSCRIPTION_FIELD[type]]["referer"] = data["referer"]

    person.save()


def nsp_confirmed_url(person, fields=None):
    if fields is None:
        fields = ["location_zip", "first_name", "last_name", "contact_phone"]
    params = {"agir_id": str(person.pk), "agir_email": str(person.email)}

    for f in fields:
        if getattr(person, f):
            params["agir_" + f] = getattr(person, f)

    url = urllib.parse.urljoin(settings.NSP_DOMAIN, "/signature-confirmee/")
    return add_query_params_to_url(url, params)
