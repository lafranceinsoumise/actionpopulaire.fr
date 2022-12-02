import json
from decimal import Decimal
from typing import Dict

from django import forms
from django.core.exceptions import ValidationError

from agir.groups.models import SupportGroup


class MoneyField(forms.DecimalField):
    def __init__(self, **kwargs):
        kwargs["decimal_places"] = 2
        for f in ["min_value", "max_value"]:
            if f in kwargs:
                kwargs[f] = Decimal(kwargs[f]) / 100
        super().__init__(**kwargs)

    def prepare_value(self, value):
        if isinstance(value, int):
            return Decimal(value) / 100
        return value

    def clean(self, value):
        value = super().clean(value)
        return value and int(value * 100)


class AskAmountField(forms.IntegerField):
    def __init__(
        self, *, amount_choices=None, show_tax_credit=True, by_month=False, **kwargs
    ):
        self.show_tax_credit = show_tax_credit
        self.by_month = by_month
        self._amount_choices = amount_choices
        super().__init__(**kwargs)

        if self.min_value is not None:
            self.widget.attrs.setdefault(
                "data-min-amount-error", self.error_messages["min_value"]
            )
        if self.max_value is not None:
            self.widget.attrs.setdefault(
                "data-max-amount-error", self.error_messages["max_value"]
            )

        self.widget.attrs.setdefault("data-by-month", self.by_month)

    @property
    def amount_choices(self):
        return self._amount_choices

    @amount_choices.setter
    def amount_choices(self, amount_choices):
        self._amount_choices = amount_choices
        if self.widget:
            self.widget.attrs["data-amount-choices"] = json.dumps(self._amount_choices)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)

        if not self.show_tax_credit:
            attrs.setdefault("data-hide-tax-credit", "Y")

        if self.amount_choices is not None:
            attrs.setdefault("data-amount-choices", json.dumps(self.amount_choices))

        return attrs


AllocationsMapping = Dict[SupportGroup, int]


def serialize_allocations(allocations):
    result = []
    for allocation in allocations:
        if "group" in allocation and isinstance(allocation["group"], SupportGroup):
            allocation["group"] = str(allocation["group"].id)
        result.append(allocation)

    return json.dumps(result)


def deserialize_allocations(serialized_allocations: str, raise_if_missing=False):
    from agir.donations.allocations import get_allocation_list

    allocations = json.loads(serialized_allocations)
    allocations = get_allocation_list(allocations)
    for allocation in allocations:
        try:
            if "group" in allocation:
                allocation["group"] = SupportGroup.objects.get(
                    pk=allocation.get("group")
                )
        except SupportGroup.DoesNotExist:
            if raise_if_missing:
                raise
            pass

    return allocations


class AllocationsField(forms.Field):
    widget = forms.HiddenInput
    hidden_widget = forms.HiddenInput
    default_error_messages = {"invalid": "Format incorrect"}

    def __init__(self, *, queryset, choices=None, **kwargs):
        super().__init__(**kwargs)
        self.queryset = queryset

    def to_python(self, value) -> AllocationsMapping:
        if value in self.empty_values:
            return {}

        try:
            from agir.donations.allocations import get_allocation_list
            from agir.donations.models import AllocationModelMixin

            value = json.loads(value)
            # TODO: implement other allocation types (or remove if the field is no longer used)
            value = get_allocation_list(value, AllocationModelMixin.TYPE_GROUP)
            value = {
                self.queryset.get(pk=allocation["group"]): int(allocation["amount"])
                for allocation in value
            }
        except (ValueError, TypeError, KeyError, self.queryset.model.DoesNotExist):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        if not all((v, int) for v in value.values()):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        return value

    def prepare_value(self, value):
        if isinstance(value, dict):
            value = json.dumps(
                [{"group": str(k.pk), "amount": v} for k, v in value.items()]
            )
        return super().prepare_value(value)

    # définition d'une propriété pour être sûr que le queryset est copié (appel de .all())
    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, value):
        self._choices = [] if value is None else value
        self.widget.attrs["data-choices"] = json.dumps(
            [{"id": str(g.id), "name": g.name} for g in value]
        )
