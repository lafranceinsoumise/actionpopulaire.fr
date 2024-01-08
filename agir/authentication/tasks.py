from django.conf import settings
from django.utils import timezone
from django.utils.http import urlencode

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.lib.celery import emailing_task
from agir.api.settings import CELERY_TASK_PRIORITY_HIGH
from agir.lib.mailing import send_mosaico_email, send_template_email
from agir.lib.utils import front_url
from agir.people.actions.subscription import SUBSCRIPTION_TYPE_AP


def interleave_spaces(s, n=3):
    return " ".join([s[i : i + n] for i in range(0, len(s), n)])


@emailing_task(priority=CELERY_TASK_PRIORITY_HIGH)
def send_login_email(email, short_code, expiry_time):
    utc_expiry_time = timezone.make_aware(
        timezone.datetime.utcfromtimestamp(expiry_time), timezone.utc
    )
    local_expiry_time = timezone.localtime(utc_expiry_time)

    code = interleave_spaces(short_code)
    send_template_email(
        template_name="authentication/login_email.html",
        from_email=settings.EMAIL_FROM,
        bindings={
            "code": code,
            "expiry_time": local_expiry_time.strftime("%H:%M"),
        },
        recipients=[email],
    )


@emailing_task(priority=CELERY_TASK_PRIORITY_HIGH)
def send_no_account_email(email, subscription_type=SUBSCRIPTION_TYPE_AP, **kwargs):
    subscription_token = subscription_confirmation_token_generator.make_token(
        email=email, type=subscription_type, **kwargs
    )
    confirm_subscription_url = front_url(
        "subscription_confirm", auto_login=False, nsp=False
    )
    query_args = {
        "email": email,
        "type": subscription_type,
        **kwargs,
        "token": subscription_token,
    }
    confirm_subscription_url += "?" + urlencode(query_args)

    send_mosaico_email(
        code="UNEXISTING_EMAIL_LOGIN",
        subject="Vous n'avez pas encore de compte sur Action Populaire",
        from_email=settings.EMAIL_FROM,
        recipients=[email],
        bindings={"SUBSCRIPTION_URL": confirm_subscription_url},
    )
