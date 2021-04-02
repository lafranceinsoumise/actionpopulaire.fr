from django.contrib.contenttypes.models import ContentType
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

    person = models.ForeignKey("people.Person", on_delete=models.CASCADE)
    type = models.CharField("Type", max_length=5, choices=SUBSCRIPTION_CHOICES)
    activity_type = models.CharField(
        "Type", max_length=50, choices=Activity.TYPE_CHOICES
    )
    # type of the object reference in this field
    # is implicit by the type of the subscription
    # can be event, group, whatever...
    related_object_id = models.UUIDField(blank=True)

    class Meta:
        # only one subscription by device and by type and by object
        unique_together = [["person", "type", "activity_type", "related_object_id"]]
