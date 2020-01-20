from agir.authentication.tokens import subscription_confirmation_token_generator


def make_subscription_token(email, **kwargs):
    return subscription_confirmation_token_generator.make_token(email=email, **kwargs)
