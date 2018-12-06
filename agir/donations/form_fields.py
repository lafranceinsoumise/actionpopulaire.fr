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
