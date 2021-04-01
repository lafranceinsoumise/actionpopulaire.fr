from push_notifications import models as push_models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from agir.activity.models import Activity
from agir.lib.models import TimeStampedModel, UUIDIdentified


class PushSubscription(UUIDIdentified, TimeStampedModel):
    type = models.CharField("Type", max_length=50, choices=Activity.TYPE_CHOICES)

    # type of the object reference in this field
    # is implicit by the type of the subscription
    related_object_id = models.UUIDField(blank=True)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name="Type de périphérique"
    )
    object_id = models.IntegerField()
    device = GenericForeignKey()

    class Meta:
        # only one subscription by device and by type and by object
        unique_together = [["content_type", "object_id", "type", "related_object_id"]]


class WebPushDevice(push_models.WebPushDevice):
    settings = GenericRelation(PushSubscription, related_query_name="subscription")

    class Meta:
        proxy = True
