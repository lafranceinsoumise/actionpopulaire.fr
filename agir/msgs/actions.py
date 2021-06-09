from django.db.models import (
    Exists,
    OuterRef,
    Case,
    When,
    Count,
    Subquery,
    IntegerField,
    DateTimeField,
    Max,
    F,
    Q,
)
from django.db.models.functions import Greatest

from agir.groups.models import SupportGroup
from agir.msgs.models import (
    SupportGroupMessageRecipient,
    SupportGroupMessage,
    SupportGroupMessageComment,
)


def update_recipient_message(message, recipient):
    obj, created = SupportGroupMessageRecipient.objects.update_or_create(
        message=message, recipient=recipient,
    )
    return obj, created


def get_unread_message_count(person_pk):
    unread_message_count = (
        SupportGroupMessage.objects.filter(
            deleted=False,
            supportgroup_id__in=SupportGroup.objects.active()
            .filter(memberships__person_id=person_pk)
            .values("id"),
        )
        .annotate(
            comment_count=Count(
                "comments",
                filter=(Q(comments__deleted=False) & ~Q(comments__author_id=person_pk)),
                distinct=True,
            )
        )
        .annotate(
            last_reading_date=Subquery(
                SupportGroupMessageRecipient.objects.filter(
                    recipient_id=person_pk, message_id=OuterRef("id")
                ).values("modified")[:1]
            )
        )
        .annotate(
            unread_count=Case(
                # If the message is unread, count 1 for the message plus 1 for each
                # of the message's comments
                When(last_reading_date=None, then=F("comment_count") + 1,),
                # If the message has already been read once, count 1 for each comment
                # created after the last reading date
                default=Subquery(
                    SupportGroupMessageComment.objects.filter(
                        deleted=False,
                        message_id=OuterRef("id"),
                        created__gt=OuterRef("last_reading_date"),
                    )
                    .exclude(author_id=person_pk)
                    .values("message_id")
                    .annotate(count=Count("pk"))
                    .values("count"),
                ),
            ),
        )
        .values_list("unread_count", flat=True)
    )

    return sum(filter(None, unread_message_count))
