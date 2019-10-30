import smtplib

import socket
from urllib.parse import urljoin

from celery import shared_task
from django.conf import settings
from django.urls import reverse

from agir.authentication.tokens import monthly_donation_confirmation_token_generator
from agir.donations.models import SpendingRequest
from agir.payments.models import Subscription
from ..lib.utils import front_url
from agir.lib.mailing import send_mosaico_email
from ..people.models import Person


@shared_task(max_retries=2, bind=True)
def send_donation_email(self, person_pk, template_code="DONATION_MESSAGE"):
    try:
        person = Person.objects.prefetch_related("emails").get(pk=person_pk)
    except Person.DoesNotExist:
        return

    try:
        send_mosaico_email(
            code=template_code,
            subject="Merci d'avoir donné !",
            from_email=settings.EMAIL_FROM,
            bindings={"PROFILE_LINK": front_url("personal_information")},
            recipients=[person],
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_spending_request_to_review_email(self, spending_request_pk):
    try:
        spending_request = SpendingRequest.objects.prefetch_related("group").get(
            pk=spending_request_pk
        )
    except SpendingRequest.DoesNotExist:
        return

    try:
        send_mosaico_email(
            code="SPENDING_REQUEST_TO_REVIEW_NOTIFICATION",
            subject="Nouvelle demande de dépense",
            from_email=settings.EMAIL_FROM,
            bindings={
                "SPENDING_REQUEST_NAME": spending_request.title,
                "GROUP_NAME": spending_request.group.name,
                "SPENDING_REQUEST_ADMIN_LINK": urljoin(
                    settings.API_DOMAIN,
                    reverse(
                        "admin:donations_spendingrequest_review",
                        args=[spending_request_pk],
                    ),
                ),
            },
            recipients=[settings.EMAIL_EQUIPE_FINANCE],
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_monthly_donation_confirmation_email(self, email, **kwargs):
    query_params = {
        "email": email,
        **{k: v for k, v in kwargs.items() if v is not None},
    }
    query_params["token"] = monthly_donation_confirmation_token_generator.make_token(
        **query_params
    )

    confirmation_link = front_url("monthly_donation_confirm", query=query_params)

    try:
        send_mosaico_email(
            code="CONFIRM_SUBSCRIPTION",
            subject="Finalisez votre don mensuel",
            from_email=settings.EMAIL_FROM,
            bindings={"CONFIRM_SUBSCRIPTION_LINK": confirmation_link},
            recipients=[email],
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)
