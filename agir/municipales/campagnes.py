from django.conf import settings

from agir.payments.payment_modes import PAYMENT_MODES
from agir.system_pay import AbstractSystemPayPaymentMode

_CAMPAGNES = {}


def init_campagnes():
    for config in settings.MUNICIPALES_CAMPAGNES:
        code_departement = config["code_departement"]
        slug = config["slug"]
        snake_case = "_".join(slug.split("-"))
        title_case = "".join(c.title() for c in slug.split("-"))
        payment_id = f"{snake_case}_system_pay"

        _CAMPAGNES[code_departement, slug] = {**config, "payment_mode": payment_id}

        sp_config = config["sp_config"]
        payment_mode = type(
            f"{title_case}PaymentMode",
            (AbstractSystemPayPaymentMode,),
            {
                "id": payment_id,
                "url_fragment": f"carte-{code_departement}-{slug}",
                "label": f"Prêt par carte à {config['nom_liste']}",
                "title": f"Prêt à {config['nom_liste']}",
                "sp_config": sp_config,
                "campagne": _CAMPAGNES[code_departement, slug],
            },
        )

        PAYMENT_MODES[payment_id] = payment_mode()


def get_campagne(code_departement, slug):
    return _CAMPAGNES.get((code_departement, slug))
