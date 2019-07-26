from __future__ import annotations

from typing import Callable, Mapping, Any, TypeVar

from dataclasses import dataclass
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse

PAYMENT_TYPES = {}
SUBSCRIPTION_TYPES = {}


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


@dataclass
class SubscriptionType:
    id: str
    label: str
    success_view: Callable[[HttpRequest, Subscription], HttpResponse]
    failure_view: Callable[[HttpRequest, Subscription], HttpResponse] = None
    status_listener: Callable[[Subscription], None] = None
    description_template: str = None
    description_context_generator: Callable[[Payment], Mapping[str, Any]] = None


def register_subscription_type(subscription_type: SubscriptionType):
    if subscription_type.id not in PAYMENT_TYPES:
        raise ImproperlyConfigured(
            f"Every SubscriptionType must have its corresponding PaymentType."
        )
    if subscription_type.id in SUBSCRIPTION_TYPES:
        raise ImproperlyConfigured(f"SubscriptionType '{id}' already exists.")
    SUBSCRIPTION_TYPES[subscription_type.id] = subscription_type
