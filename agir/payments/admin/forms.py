from django import forms

from agir.donations.form_fields import MoneyField
from agir.payments.types import get_payment_choices


class PaymentAdminForm(forms.ModelForm):
    price = MoneyField(
        label="Modifier le prix avant le paiement",
        help_text="La modification arbitraire du montant sera enregistrée si vous validez le paiement.",
    )

    type = forms.ChoiceField(
        required=True,
        label="Type de paiement",
        help_text="Ne modifiez cette valeur que si vous savez exactement ce que vous faites.",
        choices=get_payment_choices,
    )
