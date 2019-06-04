import json
import logging

from anymail.signals import tracking
from django.dispatch import receiver


logger = logging.getLogger(__name__)


@receiver(tracking, dispatch_uid="log_anymail_tracking_events")
def log_anymail_tracking_events(sender, event, esp_name, **kwargs):
    event_fields = [
        "event_type",
        "description",
        "mta_response",
        "recipient",
        "reject_reason",
    ]

    logger.info(
        json.dumps(
            {"esp_name": esp_name, **{f: getattr(event, f, None) for f in event_fields}}
        )
    )
