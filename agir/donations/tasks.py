from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse

from agir.authentication.tokens import monthly_donation_confirmation_token_generator
from agir.donations.models import SpendingRequest
from agir.lib.celery import emailing_task
from agir.lib.mailing import send_mosaico_email
from agir.lib.utils import front_url
from agir.people.models import Person


@emailing_task
def send_donation_email(person_pk, template_code="DONATION_MESSAGE"):
    try:
        person = Person.objects.prefetch_related("emails").get(pk=person_pk)
    except Person.DoesNotExist:
        return

    send_mosaico_email(
        code=template_code,
        subject="Merci d'avoir donné !",
        from_email=settings.EMAIL_FROM,
        bindings={"PROFILE_LINK": front_url("personal_information")},
        recipients=[person],
    )


@emailing_task
def send_spending_request_to_review_email(spending_request_pk):
    try:
        spending_request = SpendingRequest.objects.prefetch_related("group").get(
            pk=spending_request_pk
        )
    except SpendingRequest.DoesNotExist:
        return

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
                    "admin:donations_spendingrequest_review", args=[spending_request_pk]
                ),
            ),
        },
        recipients=[settings.EMAIL_EQUIPE_FINANCE],
    )


@emailing_task
def send_monthly_donation_confirmation_email(email, **kwargs):
    query_params = {
        "email": email,
        **{k: v for k, v in kwargs.items() if v is not None},
    }
    query_params["token"] = monthly_donation_confirmation_token_generator.make_token(
        **query_params
    )

    confirmation_link = front_url("monthly_donation_confirm", query=query_params)

    send_mosaico_email(
        code="CONFIRM_SUBSCRIPTION",
        subject="Finalisez votre don mensuel",
        from_email=settings.EMAIL_FROM,
        bindings={"CONFIRM_SUBSCRIPTION_LINK": confirmation_link},
        recipients=[email],
    )
