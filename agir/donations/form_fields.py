import json
from decimal import Decimal

from django import forms


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


class AskAmountField(forms.DecimalField):
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
