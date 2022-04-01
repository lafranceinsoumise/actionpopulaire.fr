from django.conf import settings
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from agir.checks.models import CheckPayment
from agir.lib.celery import emailing_task
from agir.lib.mailing import send_mosaico_email
from agir.payments.payment_modes import PAYMENT_MODES


@emailing_task(post_save=True)
def send_check_information(check_id, force=False):
    check = CheckPayment.objects.get(id=check_id)
    mail_sent = check.meta.get("information_email_sent")

    if mail_sent and not force:
        return

    check_mode = PAYMENT_MODES[check.mode]

    if check_mode.warnings:
        warning_list = [
            f"<li>{conditional_escape(warning)}</li>" for warning in check_mode.warnings
        ]

        warnings = mark_safe(
            f"<p>Prenez bien garde aux points suivants :</p><ul>{''.join(warning_list)}</ul>"
        )
    else:
        warnings = ""

    bindings = {
        "TITLE": check_mode.title,
        "ORDER": check_mode.order,
        "AMOUNT": check.get_price_display(),
        "PAYMENT_ID": str(check.id),
        "ADDRESS": mark_safe(
            "<br>".join(conditional_escape(part) for part in check_mode.address)
        ),
        "ADDITIONAL_INFORMATION": check_mode.additional_information,
        "WARNINGS": warnings,
    }

    send_mosaico_email(
        code="CHECK_INFORMATION",
        subject=check_mode.title,
        from_email=settings.EMAIL_FROM,
        recipients=[check.person or check.email],
        bindings=bindings,
    )

    check.meta["information_email_sent"] = True
    check.save()
