from celery import shared_task
from django.conf import settings

from agir.lib.celery import post_save_task, emailing_task
from agir.lib.mailing import send_mosaico_email
from agir.lib.sms import send_sms, SMSSendException
from agir.lib.utils import shorten_url, front_url
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy

SMS_SENDER = "Melenchon22"


@shared_task
@post_save_task
def send_voting_proxy_request_confirmation(voting_proxy_request_pks):
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        pk__in=voting_proxy_request_pks
    )
    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist()
    voting_proxy_request = voting_proxy_requests.first()
    message = (
        "Votre demande est enregistrée. Nous vous recontacterons dès qu'un·e volontaire sera disponible pour prendre "
        "votre procuration."
    )
    send_sms(message, voting_proxy_request.contact_phone, sender=SMS_SENDER)


@shared_task
@post_save_task
def send_matching_request_to_voting_proxy(voting_proxy_pk, voting_proxy_request_pks):
    voting_proxy = VotingProxy.objects.get(pk=voting_proxy_pk)
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        pk__in=voting_proxy_request_pks
    ).order_by("voting_date")

    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist()

    voting_dates = ", ".join(
        [vpr.voting_date.strftime("%d %B") for vpr in voting_proxy_requests]
    )
    if len(voting_proxy_request_pks) > 1:
        voting_dates = "les " + voting_dates
    else:
        voting_dates = "le " + voting_dates

    link = front_url(
        "reply_to_voting_proxy_requests",
        kwargs={"pk": voting_proxy_pk},
        query={"vpr": ",".join([str(pk) for pk in voting_proxy_request_pks])},
    )
    link = shorten_url(link, secret=True, djan_url_type="M2022")
    message = (
        f"Quelqu'un près de chez vous a besoin d'une procuration {voting_dates} ! "
        f"Confirmez votre disponibilité : {link}"
    )
    send_sms(message, voting_proxy.contact_phone, sender=SMS_SENDER)


@emailing_task
@post_save_task
def send_voting_proxy_candidate_invitation_email(voting_proxy_canditate_pks):
    recipients = VotingProxy.objects.filter(pk__in=voting_proxy_canditate_pks)

    if not recipients.exists():
        raise VotingProxy.DoesNotExist()

    bindings = {
        "VOTING_PROXY_REQUEST_CREATION_LINK": front_url("new_voting_proxy"),
    }
    send_mosaico_email(
        code="VOTING_PROXY_CANDIDATE_INVITATION",
        subject="Êtes-vous disponible pour prendre une procuration ?",
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@shared_task
@post_save_task
def send_voting_proxy_request_accepted_text_messages(voting_proxy_request_pks):
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        pk__in=voting_proxy_request_pks
    ).order_by("voting_date")

    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist()

    voting_proxy_request = voting_proxy_requests.first()
    voting_dates = ",".join(
        [vpr.voting_date.strftime("%d %B") for vpr in voting_proxy_requests]
    )
    if len(voting_proxy_request_pks) > 1:
        voting_dates = "les " + voting_dates
    else:
        voting_dates = "le " + voting_dates

    try:
        link = front_url(
            "voting_proxy_request_details",
            query={"vpr": ",".join([str(pk) for pk in voting_proxy_request_pks])},
        )
        link = shorten_url(link, secret=True, djan_url_type="M2022")
        request_owner_message = (
            f"{voting_proxy_request.proxy.first_name} s’est porté-e volontaire pour voter en votre nom "
            f"{voting_dates} ! {link}"
        )
        send_sms(
            request_owner_message, voting_proxy_request.contact_phone, sender=SMS_SENDER
        )
    except SMSSendException:
        pass

    try:
        voting_proxy_message = (
            f"Vous avez accepté de voter pour {voting_proxy_request.first_name} {voting_dates}. "
            f"Nous vous préviendrons lorsque {voting_proxy_request.first_name} aura établi la procuration de vote."
        )
        send_sms(
            voting_proxy_message,
            voting_proxy_request.proxy.contact_phone,
            sender=SMS_SENDER,
        )
    except SMSSendException:
        pass


@shared_task
@post_save_task
def send_voting_proxy_information_for_request(voting_proxy_request_pk):
    voting_proxy_request = VotingProxyRequest.objects.get(pk=voting_proxy_request_pk)
    message = voting_proxy_request.get_voting_proxy_information()
    send_sms(message, voting_proxy_request.contact_phone, sender=SMS_SENDER)


@shared_task
@post_save_task
def send_voting_proxy_request_confirmed_text_messages(voting_proxy_request_pks):
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        pk__in=voting_proxy_request_pks
    ).order_by("voting_date")

    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist()

    voting_date_string = ", ".join(
        [vpr.voting_date.strftime("%d %B") for vpr in voting_proxy_requests]
    )
    voting_proxy_request = voting_proxy_requests.first()
    message = (
        f"Procuration de vote établie ({voting_date_string}) :"
        f" {voting_proxy_request.first_name} {voting_proxy_request.last_name.upper()}"
        f" - {voting_proxy_request.commune.nom if voting_proxy_request.commune else voting_proxy_request.consulate.nom}"
        f" - tél. {voting_proxy_request.contact_phone}"
    )
    if voting_proxy_request.polling_station_number:
        message += f" - bureau de vote {voting_proxy_request.polling_station_number}"
    send_sms(message, voting_proxy_request.proxy.contact_phone, sender=SMS_SENDER)
