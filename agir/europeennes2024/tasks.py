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

    full_name = f'{payment.meta["first_name"]} {payment.meta["last_name"]}'

    with default_storage.open(payment.meta["contract_path"], mode="rb") as contract:

        send_template_email(
            template_name="europeennes2024/emails/merci-pret.html",
            from_email=settings.EMAIL_FROM,
            bindings={
                "cher_preteur": SUBSTITUTIONS["cher_preteur"][
                    payment.meta.get("civilite", "O")
                ]
            },
            recipients=[person],
            attachments=[
                {
                    "filename": f"contrat_pret_{slugify(full_name, only_ascii=True)}.pdf",
                    "content": contract.read(),
                    "mimetype": "application/pdf",
                }
            ],
        )


@emailing_task()
def envoyer_email_don(payment_id):
    payment = Payment.objects.select_related("person").get(id=payment_id)
    person = payment.person

    send_template_email(
        template_name="europeennes2024/emails/merci-don.html",
        from_email=settings.EMAIL_FROM,
        bindings={
            "cher_preteur": SUBSTITUTIONS["cher_preteur"][
                payment.meta.get("civilite", "O")
            ]
        },
        recipients=[person],
    )
