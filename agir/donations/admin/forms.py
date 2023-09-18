from django import forms

from agir.donations.models import SpendingRequest


class HandleRequestForm(forms.Form):
    comment = forms.CharField(
        label="Commentaire", widget=forms.Textarea, required=False
    )
    status = forms.ChoiceField(
        label="Décision",
        widget=forms.RadioSelect,
        required=True,
        choices=(
            (SpendingRequest.Status.VALIDATED, "J'approuve la demande"),
            (
                SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION,
                "Des informations supplémentaires sont nécessaires",
            ),
            (SpendingRequest.Status.REFUSED, "La demande n'est pas admissible"),
        ),
    )
