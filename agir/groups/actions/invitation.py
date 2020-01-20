from agir.authentication.tokens import (
    invitation_confirmation_token_generator,
    abusive_invitation_report_token_generator,
)
from agir.lib.utils import front_url


def make_invitation_link(person_id, group_id):
    if hasattr(person_id, "id"):
        person_id = person_id.id
    if hasattr(group_id, "id"):
        group_id = group_id.id

    token = invitation_confirmation_token_generator.make_token(
        person_id=person_id, group_id=group_id
    )

    return front_url(
        "invitation_confirmation",
        query={"person_id": person_id, "group_id": group_id, "token": token},
    )


def make_abusive_invitation_report_link(group_id, inviter_id):
    if hasattr(group_id, "id"):
        group_id = group_id.id
    if hasattr(inviter_id, "id"):
        inviter_id = inviter_id

    token = abusive_invitation_report_token_generator.make_token(
        group_id=group_id, inviter_id=inviter_id
    )

    return front_url(
        "report_invitation_abuse",
        query={"group_id": group_id, "inviter_id": inviter_id, "token": token},
    )
