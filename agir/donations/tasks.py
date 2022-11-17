from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse

from agir.authentication.tokens import monthly_donation_confirmation_token_generator
from agir.donations.models import SpendingRequest
from agir.lib.celery import (
    emailing_task,
    http_task,
)
from agir.lib.mailing import send_mosaico_email, add_params_to_urls
from agir.lib.phone_numbers import is_french_number, is_mobile_number
from agir.lib.sms import send_sms
from agir.lib.utils import front_url, generate_token_params, shorten_url
from agir.payments.types import PAYMENT_TYPES
from agir.people.models import Person
from agir.system_pay.models import SystemPaySubscription


@emailing_task(post_save=True)
def send_donation_email(person_pk, payment_type):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)
    template_code = "DONATION_MESSAGE"
    email_from = settings.EMAIL_FROM

    if (
        payment_type in PAYMENT_TYPES
        and hasattr(PAYMENT_TYPES[payment_type], "email_from")
        and PAYMENT_TYPES[payment_type].email_from
    ):
        email_from = PAYMENT_TYPES[payment_type].email_from

    if (
        payment_type in PAYMENT_TYPES
        and hasattr(PAYMENT_TYPES[payment_type], "email_template_code")
        and PAYMENT_TYPES[payment_type].email_template_code
    ):
        template_code = PAYMENT_TYPES[payment_type].email_template_code

    send_mosaico_email(
        code=template_code,
        subject="Merci d'avoir donné !",
        from_email=email_from,
        bindings={"PROFILE_LINK": front_url("personal_information")},
        recipients=[person],
    )


@emailing_task(post_save=True)
def send_spending_request_to_review_email(spending_request_pk):
    spending_request = SpendingRequest.objects.prefetch_related("group").get(
        pk=spending_request_pk
    )

    send_mosaico_email(
        code="SPENDING_REQUEST_TO_REVIEW_NOTIFICATION",
        subject="Nouvelle demande de dépense ou de remboursement",
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


@emailing_task()
def send_monthly_donation_confirmation_email(
    email, confirmation_view_name="monthly_donation_confirm", **kwargs
):
    query_params = {
        "email": email,
        **{k: v for k, v in kwargs.items() if v is not None},
    }
    query_params["token"] = monthly_donation_confirmation_token_generator.make_token(
        **query_params
    )

    confirmation_link = front_url(confirmation_view_name, query=query_params)

    send_mosaico_email(
        code="CONFIRM_SUBSCRIPTION_LFI",
        subject="Finalisez votre don mensuel",
        from_email=settings.EMAIL_FROM_LFI,
        bindings={"CONFIRM_SUBSCRIPTION_LINK": confirmation_link},
        recipients=[email],
    )


@emailing_task(post_save=True)
def send_expiration_email_reminder(sp_subscription_pk):
    sp_subscription = SystemPaySubscription.objects.select_related(
        "subscription__person", "alias"
    ).get(pk=sp_subscription_pk)

    send_mosaico_email(
        code="CARD_EXPIRATION",
        subject="Mettez à jour votre carte bancaire !",
        from_email=settings.EMAIL_FROM,
        bindings={
            "subscription_description": sp_subscription.subscription.description,
            "renew_subscription_link": front_url("view_payments"),
            "expiry_date": sp_subscription.alias.expiry_date,
        },
        recipients=[sp_subscription.subscription.person],
    )


@http_task(post_save=True)
def send_expiration_sms_reminder(sp_subscription_pk):
    sp_subscription = SystemPaySubscription.objects.select_related(
        "subscription__person", "alias"
    ).get(pk=sp_subscription_pk)

    recipient = sp_subscription.subscription.person

    if (
        not recipient.contact_phone
        or not is_french_number(recipient.contact_phone)
        or not is_mobile_number(recipient.contact_phone)
    ):
        return

    connection_params = generate_token_params(recipient)

    url = shorten_url(
        add_params_to_urls(front_url("view_payments"), connection_params), secret=True
    )

    send_sms(
        f"Votre carte bleue arrive à expiration. Pour continuer votre don régulier à la France insoumise, "
        f"mettez là à jour : {url}\n"
        f"Merci encore de votre soutien !",
        recipient.contact_phone,
    )
