from django import forms
from django.db.models import TextChoices
from django.utils import timezone

from agir.donations.base_forms import BaseDonorForm
from agir.payments.payment_modes import PAYMENT_MODES


class Regularite(TextChoices):
    PONCTUEL = "P"
    MENSUEL = "M"
    ANNUEL = "A"


def date_prelevement(regularite):
    if regularite == Regularite.PONCTUEL:
        return {}

    prelevement = timezone.now() + timezone.timedelta(days=1)

    if regularite == Regularite.MENSUEL:
        if prelevement.day >= 28:
            return {"day_of_month": 1}
        return {"day_of_month": prelevement.day}
    return {"day_of_month": prelevement.day, "month_of_year": prelevement.month}


class PersonalInformationForm(BaseDonorForm):
    show_subscribed = False

    regularite = forms.ChoiceField(
        required=True,
        choices=Regularite.choices,
        widget=forms.HiddenInput,
    )

    def __init__(self, payments_modes=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.fields.insert(0, "regularite")

        del self.fields["declaration"]
        del self.fields["fiscal_resident"]

        regularite = self.get_initial_for_field(self.fields["regularite"], "regularite")

        if regularite != Regularite.PONCTUEL:
            del self.fields["payment_mode"]

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["regularite"] != Regularite.PONCTUEL:
            cleaned_data["payment_mode"] = PAYMENT_MODES["system_pay_ilb"]

        cleaned_data.update(date_prelevement(cleaned_data["regularite"]))

        return cleaned_data
