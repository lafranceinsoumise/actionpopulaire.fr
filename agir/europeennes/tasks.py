import smtplib
import socket
import subprocess
from pathlib import Path
from uuid import uuid4

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from slugify import slugify

from agir.europeennes.actions import save_pdf_contract
from agir.payments.models import Payment
from agir.people.actions.mailing import send_mosaico_email


def contract_path(payment):
    return f"europeennes/loans/{payment.id}/{uuid4()}.pdf"


@shared_task(bind=True)
def generate_contract(self, payment_id, force=False):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return None

    if not force and (
        "contract_path" in payment.meta or payment.status != payment.STATUS_COMPLETED
    ):
        return payment.meta["contract_path"]

    contract_information = payment.meta
    contract_information["signature_date"] = (
        timezone.now()
        .astimezone(timezone.get_default_timezone())
        .date()
        .strftime("%d/%m/%Y")
    )

    pdf_media_path = contract_path(payment)
    pdf_full_path = Path(settings.MEDIA_ROOT) / pdf_media_path

    try:
        save_pdf_contract(contract_information, pdf_full_path)
    except subprocess.TimeoutExpired as exc:
        self.retry(countdown=60, exc=exc)

    payment.meta["contract_path"] = pdf_media_path
    payment.save()

    return pdf_media_path


@shared_task(bind=True)
def send_contract_confirmation_email(self, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return None

    person = payment.person

    if "contract_path" not in payment.meta:
        raise RuntimeError(
            "Contrat non généré pour le paiement {}".format(repr(payment))
        )

    full_name = f'{payment.meta["first_name"]} {payment.meta["last_name"]}'

    try:
        with open(
            Path(settings.MEDIA_ROOT) / payment.meta["contract_path"], mode="rb"
        ) as contract:
            send_mosaico_email(
                code="CONTRACT_CONFIRMATION",
                subject="Votre contrat de prêt",
                from_email=settings.EMAIL_FROM,
                bindings={},
                recipients=[person],
                attachments=[
                    {
                        "filename": f"contrat_pret_{slugify(full_name, only_ascii=True)}.pdf",
                        "content": contract.read(),
                        "mimetype": "application/pdf",
                    }
                ],
            )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)
