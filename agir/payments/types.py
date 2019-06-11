from __future__ import annotations

from typing import Callable, Mapping, Any

from dataclasses import dataclass
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse

PAYMENT_TYPES = {}


@dataclass
class PaymentType:
    id: str
    label: str
    success_view: Callable[[HttpRequest, Payment], HttpResponse]
    failure_view: Callable[[HttpRequest, Payment], HttpResponse] = None
    status_listener: Callable[[Payment], None] = None
    description_template: str = None
    description_context_generator: Callable[[Payment], Mapping[str, Any]] = None


def register_payment_type(payment_type: PaymentType):
    if payment_type.id in PAYMENT_TYPES:
        raise ImproperlyConfigured(f"PaymentType '{id}' already exists.")
    PAYMENT_TYPES[payment_type.id] = payment_type


def get_payment_choices():
    return [(p.id, p.label) for p in PAYMENT_TYPES.values()]
