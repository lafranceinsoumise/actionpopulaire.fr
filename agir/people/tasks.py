import smtplib

import socket

import requests
from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from agir.lib.display import pretty_time_since
from agir.lib.utils import front_url
from agir.lib.mailtrain import update_person, delete_email
from agir.people.actions.mailing import send_mosaico_email
from agir.people.actions.person_forms import get_formatted_submission
from agir.authentication.subscription import (
    subscription_confirmation_token_generator,
    add_email_confirmation_token_generator,
)

from .models import Person, PersonFormSubmission, PersonEmail


@shared_task(max_retries=2, bind=True)
def send_welcome_mail(self, person_pk):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)

    try:
        send_mosaico_email(
            code="WELCOME_MESSAGE",
            subject=_("Bienvenue sur la plateforme de la France insoumise"),
            from_email=settings.EMAIL_FROM,
            bindings={"PROFILE_LINK": front_url("change_profile")},
            recipients=[person],
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_confirmation_email(self, email, **kwargs):
    if PersonEmail.objects.filter(address__iexact=email).exists():
        p = Person.objects.get_by_natural_key(email)

        try:
            send_mosaico_email(
                code="ALREADY_SUBSCRIBED_MESSAGE",
                subject=_("Vous êtes déjà inscrit !"),
                from_email=settings.EMAIL_FROM,
                bindings={
                    "PANEL_LINK": front_url("dashboard", auto_login=True),
                    "AGO": pretty_time_since(p.created),
                },
                recipients=[p],
            )
        except (smtplib.SMTPException, socket.error) as exc:
            self.retry(countdown=60, exc=exc)

        return

    subscription_token = subscription_confirmation_token_generator.make_token(
        email=email, **kwargs
    )
    confirm_subscription_url = front_url("subscription_confirm", auto_login=False)
    query_args = {"email": email, **kwargs, "token": subscription_token}
    confirm_subscription_url += "?" + urlencode(query_args)

    try:
        send_mosaico_email(
            code="SUBSCRIPTION_CONFIRMATION_MESSAGE",
            subject=_("Plus qu'un clic pour vous inscrire"),
            from_email=settings.EMAIL_FROM,
            recipients=[email],
            bindings={"CONFIRMATION_URL": confirm_subscription_url},
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_confirmation_change_email(self, new_email, user_pk, **kwargs):
    try:
        Person.objects.get(pk=user_pk)
    except Person.DoesNotExist:
        return

    subscription_token = add_email_confirmation_token_generator.make_token(
        new_email=new_email, user=user_pk
    )
    query_args = {
        "new_email": new_email,
        "user": user_pk,
        "token": subscription_token,
        **kwargs,
    }
    confirm_change_mail_url = front_url(
        "confirm_change_mail", query=query_args, auto_login=False
    )

    try:
        send_mosaico_email(
            code="CHANGE_MAIL_CONFIRMATION",
            subject="confirmer votre changement d'adresse",
            from_email=settings.EMAIL_FROM,
            recipients=[new_email],
            bindings={"CONFIRMATION_URL": confirm_change_mail_url},
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_unsubscribe_email(self, person_pk):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)

    bindings = {"MANAGE_SUBSCRIPTIONS_LINK": front_url("message_preferences")}

    try:
        send_mosaico_email(
            code="UNSUBSCRIBE_CONFIRMATION",
            subject=_("Vous avez été désabonné⋅e des emails de la France insoumise"),
            from_email=settings.EMAIL_FROM,
            recipients=[person],
            bindings=bindings,
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def update_person_mailtrain(self, person_pk):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)

    try:
        update_person(person)
    except requests.RequestException as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def delete_email_mailtrain(self, email):
    try:
        delete_email(email)
    except requests.RequestException as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_person_form_confirmation(self, submission_pk):
    try:
        submission = PersonFormSubmission.objects.get(pk=submission_pk)
    except:
        return

    person = submission.person
    form = submission.form

    bindings = {"CONFIRMATION_NOTE": mark_safe(form.confirmation_note)}

    try:
        send_mosaico_email(
            code="FORM_CONFIRMATION",
            subject=_("Confirmation"),
            from_email=settings.EMAIL_FROM,
            recipients=[person],
            bindings=bindings,
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)


@shared_task(max_retries=2, bind=True)
def send_person_form_notification(self, submission_pk):
    try:
        submission = PersonFormSubmission.objects.get(pk=submission_pk)
    except:
        return

    form = submission.form

    if form.send_answers_to is None:
        return

    person = submission.person

    pretty_submission = get_formatted_submission(submission)

    bindings = {
        "ANSWER_EMAIL": person.email,
        "FORM_NAME": form.title,
        "INFORMATIONS": mark_safe(
            render_to_string(
                "people/includes/personform_submission_data.html",
                {"submission_data": pretty_submission},
            )
        ),
    }

    try:
        send_mosaico_email(
            code="FORM_NOTIFICATION",
            subject=_("Formulaire : " + form.title),
            from_email=settings.EMAIL_FROM,
            reply_to=[person.email],
            recipients=[form.send_answers_to],
            bindings=bindings,
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)
