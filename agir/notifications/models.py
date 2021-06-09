from django.db import models

from agir.activity.models import Activity
from agir.lib.models import TimeStampedModel, UUIDIdentified


class Subscription(UUIDIdentified, TimeStampedModel):
    SUBSCRIPTION_EMAIL = "email"
    SUBSCRIPTION_PUSH = "push"
    SUBSCRIPTION_CHOICES = (
        (SUBSCRIPTION_EMAIL, "Email"),
        (SUBSCRIPTION_PUSH, "Push"),
    )

    person = models.ForeignKey(
        "people.Person",
        on_delete=models.CASCADE,
        related_name="notification_subscriptions",
    )
    membership = models.ForeignKey(
        "groups.Membership", on_delete=models.CASCADE, null=True
    )
    type = models.CharField("Type", max_length=5, choices=SUBSCRIPTION_CHOICES)
    activity_type = models.CharField(
        "Type", max_length=50, choices=Activity.TYPE_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["person", "type", "activity_type", "membership"],
                name="unique_with_membership",
            ),
            models.UniqueConstraint(
                fields=["person", "type", "activity_type"],
                condition=models.Q(membership=None),
                name="unique_without_membership",
            ),
        ]
