from collections import namedtuple
from django.core.exceptions import ImproperlyConfigured


PAYMENT_TYPES = {}


PaymentType = namedtuple('PaymentType', ['id', 'label', 'success_view', 'failure_view'])


def register_payment_type(id, label, success_view, failure_view=None):
    if id in PAYMENT_TYPES:
        raise ImproperlyConfigured(f"PaymentType '{id}' already exists.")
    PAYMENT_TYPES[id] = PaymentType(id, label, success_view, failure_view)


def get_payment_choices():
    return [(p.id, p.label) for p in PAYMENT_TYPES.values()]
