import smtplib

import socket
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from agir.lib.mailing import send_mosaico_email


def interleave_spaces(s, n=3):
    return " ".join([s[i : i + n] for i in range(0, len(s), n)])


@shared_task(max_retries=2, bind=True)
def send_login_email(self, email, short_code, expiry_time):
    utc_expiry_time = timezone.make_aware(
        timezone.datetime.utcfromtimestamp(expiry_time), timezone.utc
    )
    local_expiry_time = timezone.localtime(utc_expiry_time)

    try:
        send_mosaico_email(
            code="LOGIN_MESSAGE",
            subject="Connexion à agir.lafranceinsoumise.fr",
            from_email=settings.EMAIL_FROM,
            bindings={
                "CODE": interleave_spaces(short_code),
                "EXPIRY_TIME": local_expiry_time.strftime("%H:%M"),
            },
            recipients=[email],
        )
    except (smtplib.SMTPException, socket.error) as exc:
        self.retry(countdown=60, exc=exc)
