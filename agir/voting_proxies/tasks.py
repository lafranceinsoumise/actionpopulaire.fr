from celery import shared_task

from agir.lib.celery import post_save_task
from agir.lib.sms import send_sms
from agir.voting_proxies.models import VotingProxyRequest


@shared_task
@post_save_task
def send_voting_proxy_request_confirmation(voting_proxy_request_pks):
    if len(voting_proxy_request_pks) == 0:
        return
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
    send_sms(message, voting_proxy_request.contact_phone)
