from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import format_html_join
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from agir.lib.display import pretty_time_since
from agir.lib.utils import front_url
from agir.lib.mailtrain import update_person, delete_email
from agir.people.actions.mailing import send_mosaico_email
from agir.people.actions.person_forms import get_formatted_submission
from agir.authentication.subscription import subscription_confirmation_token_generator

from .models import Person, PersonFormSubmission, PersonEmail


@shared_task
def send_welcome_mail(person_pk):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)
    send_mosaico_email(
        code="WELCOME_MESSAGE",
        subject=_("Bienvenue sur la plateforme de la France insoumise"),
        from_email=settings.EMAIL_FROM,
        bindings={"PROFILE_LINK": front_url("change_profile")},
        recipients=[person],
    )


@shared_task
def send_confirmation_email(email, **kwargs):
    if PersonEmail.objects.filter(address__iexact=email).exists():
        p = Person.objects.get_by_natural_key(email)
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
        return

    subscription_token = subscription_confirmation_token_generator.make_token(
        email=email, **kwargs
    )
    confirm_subscription_url = front_url("subscription_confirm", auto_login=False)
    query_args = {"email": email, **kwargs, "token": subscription_token}
    confirm_subscription_url += "?" + urlencode(query_args)

    send_mosaico_email(
        code="SUBSCRIPTION_CONFIRMATION_MESSAGE",
        subject=_("Plus qu'un clic pour vous inscrire"),
        from_email=settings.EMAIL_FROM,
        recipients=[email],
        bindings={"CONFIRMATION_URL": confirm_subscription_url},
    )


@shared_task
def send_unsubscribe_email(person_pk):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)

    bindings = {"MANAGE_SUBSCRIPTIONS_LINK": front_url("message_preferences")}

    send_mosaico_email(
        code="UNSUBSCRIBE_CONFIRMATION",
        subject=_("Vous avez été désabonné⋅e des emails de la France insoumise"),
        from_email=settings.EMAIL_FROM,
        recipients=[person],
        bindings=bindings,
    )


@shared_task
def update_person_mailtrain(person_pk):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)

    update_person(person)


@shared_task
def delete_email_mailtrain(email):
    delete_email(email)


@shared_task
def send_person_form_confirmation(submission_pk):
    try:
        submission = PersonFormSubmission.objects.get(pk=submission_pk)
    except:
        return

    person = submission.person
    form = submission.form

    bindings = {"CONFIRMATION_NOTE": mark_safe(form.confirmation_note)}

    send_mosaico_email(
        code="FORM_CONFIRMATION",
        subject=_("Confirmation"),
        from_email=settings.EMAIL_FROM,
        recipients=[person],
        bindings=bindings,
    )


@shared_task
def send_person_form_notification(submission_pk):
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

    send_mosaico_email(
        code="FORM_NOTIFICATION",
        subject=_("Formulaire : " + form.title),
        from_email=settings.EMAIL_FROM,
        reply_to=[person.email],
        recipients=[form.send_answers_to],
        bindings=bindings,
    )
