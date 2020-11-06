from dataclasses import dataclass

from django.conf import settings

from agir.authentication.tokens import subscription_confirmation_token_generator


def make_subscription_token(email, **kwargs):
    return subscription_confirmation_token_generator.make_token(email=email, **kwargs)


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
    SUBSCRIPTION_TYPE_NSP: "is_nsp",
}


@dataclass
class SubscriptionMessageInfo:
    code: str
    subject: str
    from_email: str = settings.EMAIL_FROM


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
            "Plus qu'un clic pour valider votre soutien !",
            "nepasrepondre@noussommespour.fr",
        )
    },
    SUBSCRIPTION_TYPE_EXTERNAL: {},
}
