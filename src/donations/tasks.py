from celery import shared_task
from django.conf import settings

from lib.utils import front_url
from people.actions.mailing import send_mosaico_email
from people.models import Person


@shared_task
def send_donation_email(person_pk):
    person = Person.objects.prefetch_related('emails').get(pk=person_pk)
    send_mosaico_email(
        code='DONATION_MESSAGE',
        subject="Merci d'avoir donné !",
        from_email=settings.EMAIL_FROM,
        bindings={'PROFILE_LINK': front_url('change_profile')},
        recipients=[person]
    )
