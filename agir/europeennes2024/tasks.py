from django.conf import settings
from django.core.files.storage import default_storage
from slugify import slugify

from agir.lib.celery import emailing_task
from agir.lib.mailing import send_template_email
from agir.loans.display import SUBSTITUTIONS
from agir.payments.models import Payment
from agir.payments.types import PAYMENT_TYPES


@emailing_task()
def envoyer_email_pret(payment_id):
    payment = Payment.objects.select_related("person").get(id=payment_id)
    person = payment.person

    if "contract_path" not in payment.meta:
        raise RuntimeError(
            "Contrat non généré pour le paiement {}".format(repr(payment))
        )

    nom_complet = f'{payment.meta["first_name"]} {payment.meta["last_name"]}'
    prenom = payment.first_name.capitalize()
    cher = SUBSTITUTIONS["cher"][payment.meta.get("civilite", "O")]
    adresse = f"{cher} {prenom}"

    with default_storage.open(payment.meta["contract_path"], mode="rb") as contract:

        send_template_email(
            template_name="europeennes2024/emails/merci-pret.html",
            from_email=settings.EMAIL_FROM,
            bindings={"cher_preteur": adresse},
            recipients=[person],
            attachments=[
                {
                    "filename": f"contrat_pret_{slugify(nom_complet, only_ascii=True)}.pdf",
                    "content": contract.read(),
                    "mimetype": "application/pdf",
                }
            ],
        )


@emailing_task()
def envoyer_email_don(payment_id):
    payment = Payment.objects.select_related("person").get(id=payment_id)

    prenom = payment.first_name.capitalize()
    cher = SUBSTITUTIONS["cher"][payment.meta.get("civilite", "O")]
    adresse = f"{cher} {prenom}"

    send_template_email(
        template_name="europeennes2024/emails/merci-don.html",
        from_email=settings.EMAIL_FROM,
        bindings={"cher_donneur": adresse},
        recipients=[payment.person],
    )
