from django.db.models import (
    OuterRef,
    Case,
    When,
    Count,
    Subquery,
    IntegerField,
    F,
    Exists,
    Q,
    Max,
    DateTimeField,
    Prefetch,
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


def get_viewables_messages(person):
    return (
        SupportGroupMessage.objects.active()
        .annotate(
            has_required_membership_type=Exists(
                person.memberships.filter(
                    supportgroup_id=OuterRef("supportgroup_id"),
                    membership_type__gte=OuterRef("required_membership_type"),
                )
            )
        )
        .filter(Q(author_id=person.id) | Q(has_required_membership_type=True))
    )


def get_viewable_messages_ids(person):
    message_ids = get_viewables_messages(person).values_list("id", flat=True)
    return list(set(message_ids))


def get_unread_message_count(person):
    if not isinstance(person, Person):
        return 0

    allowed_message_ids = get_viewable_messages_ids(person)

    if len(allowed_message_ids) == 0:
        return 0

    unread_comment_count_subquery = Coalesce(
        Subquery(
            SupportGroupMessageComment.objects.active()
            .filter(
                message_id=OuterRef("id"),
                created__gt=Greatest(
                    OuterRef("last_reading_date"),
                    OuterRef("membership_created"),
                    OuterRef("created"),
                ),
            )
            .exclude(
                author_id=person.id,
            )
            .values("message_id")
            .annotate(count=Count("pk"))
            .values("count"),
            output_field=IntegerField(),
        ),
        0,
    )

    unread_message_count = (
        SupportGroupMessage.objects.filter(pk__in=allowed_message_ids)
        .exclude(id__in=person.messages_muted.values_list("pk", flat=True))
        .annotate(
            membership_created=Subquery(
                Membership.objects.filter(
                    supportgroup_id=OuterRef("supportgroup_id"),
                    person_id=person.id,
                ).values("created")[:1]
            )
        )
        .annotate(
            last_reading_date=Subquery(
                SupportGroupMessageRecipient.objects.filter(
                    recipient_id=person.id, message_id=OuterRef("id")
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
        SupportGroupMessageComment.objects.active()
        .filter(
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


def get_user_messages(person):
    return (
        SupportGroupMessage.objects.with_serializer_prefetch()
        .filter(id__in=get_viewable_messages_ids(person))
        .prefetch_related(
            Prefetch(
                "comments",
                queryset=SupportGroupMessageComment.objects.filter(
                    id__in=Subquery(
                        SupportGroupMessageComment.objects.active()
                        .order_by("-created")
                        .values_list("id", flat=True)[:1]
                    )
                ),
                to_attr="_pf_last_comment",
            ),
        )
        .annotate(
            is_unread=Case(
                When(
                    created__lt=Subquery(
                        Membership.objects.filter(
                            supportgroup_id=OuterRef("supportgroup_id"),
                            person_id=person.pk,
                        ).values("created")[:1]
                    ),
                    then=False,
                ),
                default=~Exists(
                    SupportGroupMessageRecipient.objects.filter(
                        recipient=person, message_id=OuterRef("id")
                    )
                ),
            )
        )
        .annotate(
            last_update=Greatest(
                Max("comments__created"), "created", output_field=DateTimeField()
            )
        )
        .distinct()
        .order_by("-last_update", "-created")
    )
