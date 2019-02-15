from django.db import models

from agir.donations.form_fields import MoneyField


class BalanceField(models.IntegerField):
    def formfield(self, **kwargs):
        return super().formfield(**{"form_class": MoneyField, **kwargs})


class AmountField(models.PositiveIntegerField):
    def formfield(self, **kwargs):
        return super().formfield(**{"form_class": MoneyField, **kwargs})
