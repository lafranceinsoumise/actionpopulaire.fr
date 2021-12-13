from django.db.models import (
    OuterRef,
    Case,
    When,
    Count,
    Subquery,
    IntegerField,
    F,
)
from django.db.models.functions import Greatest, Coalesce

from agir.groups.models import SupportGroup, Membership
from agir.msgs.models import (
    SupportGroupMessageRecipient,
    SupportGroupMessage,
    SupportGroupMessageComment,
)
from agir.people.models import Person


def update_recipient_message(message, recipient):
    obj, created = SupportGroupMessageRecipient.objects.update_or_create(
        message=message,
        recipient=recipient,
    )
    return obj, created


def get_unread_message_count(person_pk):
    unread_comment_count_subquery = Coalesce(
        Subquery(
            SupportGroupMessageComment.objects.filter(
                deleted=False,
                author__role__is_active=True,
                message_id=OuterRef("id"),
                created__gt=Greatest(
                    OuterRef("last_reading_date"),
                    OuterRef("membership_created"),
                    OuterRef("created"),
                ),
            )
            .exclude(
                author_id=person_pk,
            )
            .values("message_id")
            .annotate(count=Count("pk"))
            .values("count"),
            output_field=IntegerField(),
        ),
        0,
    )

    # Filter messages where person is not allowed (not author, not in required membership)
    messages = SupportGroupMessage.objects.filter(
        deleted=False,
        author__role__is_active=True,
        supportgroup_id__in=SupportGroup.objects.active()
        .filter(memberships__person_id=person_pk)
        .values("id"),
    )
    if not isinstance(person_pk, Person):
        person_pk = Person.objects.get(pk=person_pk)
    messages_allowed_id = [
        msg.id
        for msg in messages
        if person_pk.role.has_perm("msgs.view_supportgroupmessage", msg)
    ]

    unread_message_count = (
        SupportGroupMessage.objects.filter(pk__in=messages_allowed_id)
        .annotate(
            membership_created=Subquery(
                Membership.objects.filter(
                    supportgroup_id=OuterRef("supportgroup_id"),
                    person_id=person_pk,
                ).values("created")[:1]
            )
        )
        .annotate(
            last_reading_date=Subquery(
                SupportGroupMessageRecipient.objects.filter(
                    recipient_id=person_pk, message_id=OuterRef("id")
                ).values("modified")[:1]
            )
        )
        .annotate(unread_comment_count=unread_comment_count_subquery)
        .annotate(
            unread_count=Case(
                # If the message is unread and has been created after the person has joined the group,
                # count 1 for the message plus 1 for each of the message's comments
                When(
                    last_reading_date=None,
                    created__gt=F("membership_created"),
                    then=F("unread_comment_count") + 1,
                ),
                # If the message has already been read once, count 1 for each comment
                # created after the last reading date and after the person has joined
                # the group
                default=F("unread_comment_count"),
            ),
        )
        .values_list("unread_count", flat=True)
    )

    return sum(unread_message_count)


def get_message_unread_comment_count(person_pk, message_pk):
    return (
        SupportGroupMessageComment.objects.filter(
            deleted=False,
            author__role__is_active=True,
            message_id=message_pk,
            message__supportgroup_id__in=SupportGroup.objects.active()
            .filter(memberships__person_id=person_pk)
            .values("id"),
        )
        .exclude(author_id=person_pk)
        .annotate(
            membership_created=Subquery(
                Membership.objects.filter(
                    supportgroup_id=OuterRef("message__supportgroup_id"),
                    person_id=person_pk,
                ).values("created")[:1]
            )
        )
        .annotate(
            last_reading_date=Subquery(
                SupportGroupMessageRecipient.objects.filter(
                    recipient_id=person_pk, message_id=message_pk
                ).values("modified")[:1]
            )
        )
        .filter(
            created__gt=Greatest(
                "last_reading_date",
                "membership_created",
                "message__created",
            ),
        )
    ).count()
