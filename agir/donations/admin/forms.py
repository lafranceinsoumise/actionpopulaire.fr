from django import forms

from agir.donations.models import SpendingRequest, Operation


class HandleRequestForm(forms.Form):
    comment = forms.CharField(label="Commentaire", widget=forms.Textarea, required=True)
    status = forms.ChoiceField(
        label="Décision",
        widget=forms.RadioSelect,
        required=True,
        choices=(
            (SpendingRequest.STATUS_VALIDATED, "J'approuve la demande"),
            (
                SpendingRequest.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
                "Des informations supplémentaires sont nécessaires",
            ),
            (SpendingRequest.STATUS_REFUSED, "La demande n'est pas admissible"),
        ),
    )
