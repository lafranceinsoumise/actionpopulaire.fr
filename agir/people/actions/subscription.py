from agir.authentication.tokens import subscription_confirmation_token_generator


def make_subscription_token(email, **kwargs):
    return subscription_confirmation_token_generator.make_token(email=email, **kwargs)


SUBSCRIPTION_TYPE_LFI = "LFI"
SUBSCRIPTION_TYPE_NSP = "NSP"
SUBSCRIPTION_TYPE_EXT = "EXT"
SUBSCRIPTION_TYPE_CHOICES = (
    (SUBSCRIPTION_TYPE_LFI, "LFI",),
    (SUBSCRIPTION_TYPE_NSP, "NSP",),
    (SUBSCRIPTION_TYPE_EXT, "EXT"),
)
SUBSCRIPTION_FIELD = {
    SUBSCRIPTION_TYPE_LFI: "is_insoumise",
    SUBSCRIPTION_TYPE_NSP: "is_nsp",
}
SUBSCRIPTIONS_EMAILS = {
    SUBSCRIPTION_TYPE_LFI: {
        "confirmation": (
            "SUBSCRIPTION_CONFIRMATION_LFI_MESSAGE",
            "Plus qu'un clic pour vous inscrire",
        ),
        "already_subscribed": (
            "ALREADY_SUBSCRIBED_LFI_MESSAGE",
            "Vous êtes déjà inscrits !",
        ),
        "welcome": "WELCOME_LFI_MESSAGE",
    },
    SUBSCRIPTION_TYPE_NSP: {"confirmation": ("TODO CODE", "TODO SUJET",)},
    SUBSCRIPTION_TYPE_EXT: {},
}
