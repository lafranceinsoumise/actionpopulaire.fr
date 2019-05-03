import smtplib

import socket
from celery import shared_task
from django.conf import settings

from ..lib.utils import front_url
from ..people.actions.mailing import send_mosaico_email
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
