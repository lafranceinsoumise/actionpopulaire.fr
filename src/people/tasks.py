from django.utils.translation import ugettext as _
from django.conf import settings

from celery import shared_task

from lib.mails import send_mosaico_email
from front.utils import front_url

from .models import Person


@shared_task
def send_welcome_mail(person_pk):
    person = Person.objects.get(pk=person_pk)

    send_mosaico_email(
        code='WELCOME_MESSAGE',
        subject=_("Bienvenue sur la plateforme de la France insoumise"),
        from_email=settings.EMAIL_FROM,
        recipients=[person.email]
    )


@shared_task
def send_unsubscribe_email(person_pk):
    person = Person.objects.get(pk=person_pk)

    bindings = {
        "MANAGE_SUBSCRIPTIONS_LINK": front_url('message_preferences'),
    }

    send_mosaico_email(
        code='UNSUBSCRIBE_CONFIRMATION',
        subject=_('Vous avez été désabonné⋅e des emails de la France insoumise'),
        from_email=settings.EMAIL_FROM,
        recipients=[person.email],
        bindings=bindings
    )
