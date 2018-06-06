from celery import shared_task
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from agir.lib.utils import front_url
from agir.lib.mailtrain import update_person
from agir.people.actions.mailing import send_mosaico_email
from .models import Person, PersonFormSubmission


@shared_task
def send_welcome_mail(person_pk):
    person = Person.objects.prefetch_related('emails').get(pk=person_pk)
    send_mosaico_email(
        code='WELCOME_MESSAGE',
        subject=_("Bienvenue sur la plateforme de la France insoumise"),
        from_email=settings.EMAIL_FROM,
        bindings={'PROFILE_LINK': front_url('change_profile')},
        recipients=[person]
    )


@shared_task
def send_unsubscribe_email(person_pk):
    person = Person.objects.prefetch_related('emails').get(pk=person_pk)

    bindings = {
        "MANAGE_SUBSCRIPTIONS_LINK": front_url('message_preferences'),
    }

    send_mosaico_email(
        code='UNSUBSCRIBE_CONFIRMATION',
        subject=_('Vous avez été désabonné⋅e des emails de la France insoumise'),
        from_email=settings.EMAIL_FROM,
        recipients=[person],
        bindings=bindings
    )

@shared_task
def update_mailtrain(person_pk):
    person = Person.objects.prefetch_related('emails').get(pk=person_pk)

    update_person(person)


@shared_task
def send_person_form_confirmation(submission_pk):
    try:
        submission = PersonFormSubmission.objects.get(pk=submission_pk)
    except :
        return

    person = submission.person
    form = submission.form

    bindings = {
        "CONFIRMATION_NOTE": mark_safe(form.confirmation_note)
    }

    send_mosaico_email(
        code='FORM_CONFIRMATION',
        subject=_("Confirmation"),
        from_email=settings.EMAIL_FROM,
        recipients=[person],
        bindings=bindings,
    )

@shared_task
def send_person_form_notification(submission_pk):
    try:
        submission = PersonFormSubmission.objects.get(pk=submission_pk)
    except :
        return

    form = submission.form

    if form.send_answers_to is None:
        return

    person = submission.person

    fields = [field for fieldset in form.custom_fields for field in fieldset['fields']]
    data = {(field.get('label') or Person._meta.get_field(field['id']).verbose_name): submission.data.get(field['id'], 'NA') for field in fields}
    data['Date'] = submission.modified

    bindings = {
        "ANSWER_EMAIL": person.email,
        "FORM_NAME": form.title,
        "INFORMATIONS": mark_safe('<br>'.join([f'{key} : {data[key]}' for key in data.keys()]))
    }

    send_mosaico_email(
        code='FORM_NOTIFICATION',
        subject=_("Formulaire : " + form.title),
        from_email=settings.EMAIL_FROM,
        reply_to=[person.email],
        recipients=[form.send_answers_to],
        bindings=bindings,
    )
