from django.db.models import Sum

from agir.cagnottes.apps import CagnottesConfig
from agir.payments.models import Payment


def montant_cagnotte(cagnotte):
    return (
        Payment.objects.completed()
        .filter(type=CagnottesConfig.PAYMENT_TYPE, meta__cagnotte=cagnotte.id)
        .aggregate(total=Sum("price"))["total"]
        or 0
    )
