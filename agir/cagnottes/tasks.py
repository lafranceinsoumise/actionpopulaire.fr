from django.conf import settings

from agir.cagnottes.apps import CagnottesConfig
from agir.cagnottes.models import Cagnotte
from agir.lib.celery import emailing_task
from agir.lib.mailing import send_template_email
from agir.payments.models import Payment


@emailing_task(post_save=True)
def envoyer_email_remerciement(payment_id):
    payment = Payment.objects.select_related("person").get(id=payment_id)

    if payment.type != CagnottesConfig.PAYMENT_TYPE or "cagnotte" not in payment.meta:
        return

    cagnotte = Cagnotte.objects.get(id=payment.meta["cagnotte"])

    person = payment.person
    from_ = cagnotte.expediteur_email or settings.EMAIL_FROM

    send_template_email(
        template_name="cagnottes/message_remerciements.html",
        from_email=from_,
        bindings={"cagnotte": cagnotte},
        recipients=[person],
    )
