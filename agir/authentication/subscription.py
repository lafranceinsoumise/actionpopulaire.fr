from .crypto import (
    SubscriptionConfirmationTokenGenerator,
    AddEmailConfirmationTokenGenerator,
)


subscription_confirmation_token_generator = SubscriptionConfirmationTokenGenerator(7)
add_email_confirmation_token_generator = AddEmailConfirmationTokenGenerator(7)
