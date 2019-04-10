from .crypto import (
    SubscriptionConfirmationTokenGenerator,
    AddEmailConfirmationTokenGenerator,
    MergeAccountTokenGenerator,
)


subscription_confirmation_token_generator = SubscriptionConfirmationTokenGenerator(7)
add_email_confirmation_token_generator = AddEmailConfirmationTokenGenerator(7)
merge_account_token_generator = MergeAccountTokenGenerator(7)
