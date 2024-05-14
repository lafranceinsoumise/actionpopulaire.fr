from django.http import Http404

from agir.payments.types import PaymentType


def not_found(request, payment):
    raise Http404()


class LegacyPaymentType(PaymentType):
    """Un type de paiement anciennement utilisé.

    Permet de définir des types de paiement qui ne peuvent plus être effectués, mais qui permettent
    la consultation dans action populaire.
    """

    def __init__(self, **kwargs):
        super().__init__(
            success_view=not_found,
            **kwargs,
        )
