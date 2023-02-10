from django.core.exceptions import ValidationError
from django.db.models import Sum

from agir.api.redis import get_auth_redis_client
from agir.cagnottes.apps import CagnottesConfig
from agir.cagnottes.models import Cagnotte
from agir.payments.models import Payment


def redis_key(cagnotte: Cagnotte):
    return f"Cagnotte:{cagnotte.slug}:montant"


def recalculer_montant_cagnotte(cagnotte):
    return (
        Payment.objects.completed()
        .filter(type=CagnottesConfig.PAYMENT_TYPE, meta__cagnotte=cagnotte.id)
        .aggregate(total=Sum("price"))["total"]
        or 0
    )


def montant_cagnotte(cagnotte):
    raw_value = get_auth_redis_client().get(redis_key(cagnotte))

    try:
        return int(raw_value)
    except (ValueError, TypeError):
        return 0


def ajouter_compteur(payment: Payment):
    if "cagnotte" not in payment.meta:
        return
    try:
        cagnotte = Cagnotte.objects.get(id=payment.meta["cagnotte"])
    except (Cagnotte.DoesNotExist, ValidationError, ValueError, TypeError):
        return

    client = get_auth_redis_client()

    client.incr(redis_key(cagnotte), payment.price)


def rafraichir_compteur(cagnotte):
    montant = recalculer_montant_cagnotte(cagnotte)
    get_auth_redis_client().set(redis_key(cagnotte), montant)
