from django import forms

from agir.donations.models import SpendingRequest


class HandleRequestForm(forms.Form):
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
    comment = forms.CharField(
        label="Commentaire",
        widget=forms.Textarea,
        required=False,
        help_text="Le commentaire sera visible par les gestionnaires financiers sur la page de la demande",
    )
    bank_transfer_label = forms.CharField(
        label="Libellé de virement", required=False, max_length=200
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
