from agir.api.redis import get_auth_redis_client


def incrementer_compteur(compteur, montant):
    client = get_auth_redis_client()

    cle = f"Europeennes2024:{compteur}:montant"
    client.incr(cle, montant)


def montant_compteur(compteur):
    raw_value = get_auth_redis_client().get(f"Europeennes2024:{compteur}:montant")

    try:
        return int(raw_value)
    except (ValueError, TypeError):
        return 0
