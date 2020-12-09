import urllib.parse
from dataclasses import dataclass

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.elus.models import types_elus, STATUT_A_VERIFIER_INSCRIPTION
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
            "Nous sommes pour <nepasrepondre@noussommespour.fr>",
        )
    },
    SUBSCRIPTION_TYPE_EXTERNAL: {},
}
SUBSCRIPTION_NEWSLETTERS = {
    SUBSCRIPTION_TYPE_LFI: {Person.NEWSLETTER_LFI},
    SUBSCRIPTION_TYPE_NSP: set(),
    SUBSCRIPTION_TYPE_EXTERNAL: set(),
}


def save_subscription_information(person, type, data):
    person_fields = set(f.name for f in Person._meta.get_fields())

    # mise à jour des différents champs
    for f in person_fields.intersection(data):
        # On ne remplace que les champs vides de la personne
        setattr(person, f, getattr(person, f) or data[f])

    person.newsletters = list(SUBSCRIPTION_NEWSLETTERS[type].union(person.newsletters))

    if type in SUBSCRIPTION_FIELD and not getattr(person, SUBSCRIPTION_FIELD[type]):
        setattr(person, SUBSCRIPTION_FIELD[type], True)
    subscriptions = person.meta.setdefault("subscriptions", {})
    if type not in subscriptions:
        subscriptions[type] = {"date": timezone.now().isoformat()}
        if referrer_id := data.get("referrer", data.get("referer")):
            try:
                p = Person.objects.get(referrer_id=referrer_id)
            except Person.DoesNotExist:
                pass
            else:
                subscriptions[type]["referrer"] = str(p.pk)

    if data.get("mandat"):
        subscriptions[type]["mandat"] = data["mandat"]

    with transaction.atomic():
        if data.get("mandat"):
            try:
                types_elus[data["mandat"]].objects.get_or_create(
                    person=person, defaults={"statut": STATUT_A_VERIFIER_INSCRIPTION}
                )
            except types_elus[data["mandat"]].MultipleObjectsReturned:
                pass

        person.save()


def nsp_confirmed_url(id, data):
    params = {"agir_id": str(id)}
    params.update({"agir_{k}": v for k, v in data.items()})
    url = urllib.parse.urljoin(settings.NSP_DOMAIN, "/signature-confirmee/")
    return add_query_params_to_url(url, params, as_fragment=True)
