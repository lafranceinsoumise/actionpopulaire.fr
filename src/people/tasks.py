from celery import shared_task
from django.utils.translation import ugettext as _

from lib.mails import get_mosaico_email, send_mail

from .models import Person


@shared_task
def send_welcome_mail(person_pk):
    person = Person.objects.get(pk=person_pk)

    message = get_mosaico_email(code='WELCOME_MAIL', recipient=person.email)

    send_mail(_("Bienvenue à la France insoumise"), message, "noreply@lafranceinsoumise.fr", [person.email])
