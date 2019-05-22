from .crypto import (
    SubscriptionConfirmationSignatureGenerator,
    AddEmailConfirmationSignatureGenerator,
    MergeAccountSignatureGenerator,
    InvitationConfirmationSignatureGenerator,
    AbusiveInvitationReportSignatureGenerator,
)


subscription_confirmation_token_generator = SubscriptionConfirmationSignatureGenerator(
    7
)
add_email_confirmation_token_generator = AddEmailConfirmationSignatureGenerator(7)
merge_account_token_generator = MergeAccountSignatureGenerator(7)
invitation_confirmation_token_generator = InvitationConfirmationSignatureGenerator(7)
abusive_invitation_report_token_generator = AbusiveInvitationReportSignatureGenerator(7)
