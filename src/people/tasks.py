from django.utils.translation import ugettext as _
from django.conf import settings

from celery import shared_task

from lib.mails import send_mosaico_email

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
