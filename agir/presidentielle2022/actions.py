from django.db.models import Sum

from agir.payments.models import Payment
from agir.presidentielle2022.apps import Presidentielle2022Config


def get_aggregates():
    return (
        Payment.objects.completed()
        .filter(
            type__in=[
                Presidentielle2022Config.DONATION_PAYMENT_TYPE,
                Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
            ]
        )
        .aggregate(totalAmount=Sum("price"))
    )
