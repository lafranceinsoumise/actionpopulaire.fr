from agir.msgs.models import SupportGroupMessageRecipient


def update_recipient_message(message, recipient):
    obj, created = SupportGroupMessageRecipient.objects.update_or_create(
        message=message, recipient=recipient,
    )
    return obj, created
