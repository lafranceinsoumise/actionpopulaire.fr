import subprocess
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.utils import timezone
from slugify import slugify

from agir.lib.celery import retriable_task, emailing_task
from agir.lib.mailing import send_mosaico_email
from agir.loans.actions import generate_pdf_contract
from agir.loans.display import SUBSTITUTIONS
from agir.loans.loan_config import LoanConfiguration
from agir.payments.models import Payment
from agir.payments.types import PAYMENT_TYPES
from agir.people.models import Document


@retriable_task(start=1, retry_on=(subprocess.TimeoutExpired, Payment.DoesNotExist))
def generate_contract(payment_id, force=False):
    payment = Payment.objects.get(id=payment_id)
    loan_configuration: LoanConfiguration = PAYMENT_TYPES.get(payment.type)
    if loan_configuration is None:
        return None

    contract_path = loan_configuration.contract_path(payment)

    if not force and payment.status != Payment.STATUS_COMPLETED:
        raise ValueError(f"Paiement n°{payment_id} n'a pas été terminé.")

    if not force and ("contract_path" in payment.meta):
        return payment.meta.get("contract_path")

    contract_information = payment.meta.copy()
    contract_information["payment_mode"] = payment.mode
    contract_generation_datetime = timezone.now()
    contract_information["contract_generation_datetime"] = (
        contract_generation_datetime.isoformat()
    )

    pdf_content = generate_pdf_contract(
        payment_type=loan_configuration,
        contract_information=contract_information,
    )

    actual_path = default_storage.save(contract_path, ContentFile(pdf_content))

    with transaction.atomic():
        payment.meta["contract_path"] = actual_path
        payment.save()
        Document.objects.create(
            titre=f"{loan_configuration.label} (contrat)",
            person=payment.person,
            date=contract_generation_datetime,
            type=Document.Type.CONTRAT_PRET,
            fichier=actual_path,
        )

    return contract_path


@emailing_task(post_save=True)
def send_contract_confirmation_email(payment_id):
    payment = Payment.objects.get(id=payment_id)
    person = payment.person

    if "contract_path" not in payment.meta:
        raise RuntimeError(
            "Contrat non généré pour le paiement {}".format(repr(payment))
        )

    full_name = f'{payment.meta["first_name"]} {payment.meta["last_name"]}'

    with open(
        Path(settings.MEDIA_ROOT) / payment.meta["contract_path"], mode="rb"
    ) as contract:
        send_mosaico_email(
            code="CONTRACT_CONFIRMATION",
            subject="Votre contrat de prêt",
            from_email=settings.EMAIL_FROM,
            bindings={
                "CHER_PRETEUR": SUBSTITUTIONS["cher_preteur"][
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
