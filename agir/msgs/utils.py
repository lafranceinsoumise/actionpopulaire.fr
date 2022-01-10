from django.db.models import (
    Case,
    DateTimeField,
    Exists,
    Max,
    OuterRef,
    When,
    Subquery,
    Q,
)
from django.db.models.functions import Greatest
from agir.groups.models import Membership, SupportGroup
from agir.msgs.models import (
    SupportGroupMessage,
    SupportGroupMessageRecipient,
)


# Get messages where user is author or allowed in group
def get_user_messages(person):

    person_groups = (
        SupportGroup.objects.active().filter(memberships__person=person).values("id")
    )

    user_message = SupportGroupMessageRecipient.objects.filter(
        recipient=person, message_id=OuterRef("id")
    )

    # Get messages where person is author or is in group
    group_messages = (
        SupportGroupMessage.queryset.filter(
            (Q(supportgroup_id__in=person_groups) | Q(author=person))
            & Q(author__role__is_active=True)
        )
        .select_related("supportgroup", "author")
        .prefetch_related("comments")
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
                default=~Exists(user_message),
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

    # Filter messages where person is not in allowed membership types
    return [
        msg
        for msg in group_messages
        if person.role.has_perm("msgs.view_supportgroupmessage", msg)
    ]
