from collections import namedtuple
from django.core.exceptions import ImproperlyConfigured


PAYMENT_TYPES = {}


PaymentType = namedtuple(
    "PaymentType",
    [
        "id",
        "label",
        "success_view",
        "failure_view",
        "status_listener",
        "description_template",
        "description_context_generator",
    ],
)


def register_payment_type(
    id,
    label,
    success_view,
    failure_view=None,
    status_listener=None,
    description_template=None,
    description_context_generator=None,
):
    if id in PAYMENT_TYPES:
        raise ImproperlyConfigured(f"PaymentType '{id}' already exists.")
    PAYMENT_TYPES[id] = PaymentType(
        id,
        label,
        success_view,
        failure_view,
        status_listener,
        description_template,
        description_context_generator,
    )


def get_payment_choices():
    return [(p.id, p.label) for p in PAYMENT_TYPES.values()]
