import json
from email.mime.text import MIMEText

from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils.html import format_html, escape

from agir.lib.celery import post_save_task, emailing_task
from agir.lib.mailing import send_mosaico_email
from agir.lib.sms import send_sms
from agir.lib.sms.common import SMSSendException, to_7bit_string
from agir.lib.utils import shorten_url, front_url
from agir.voting_proxies.models import VotingProxyRequest, VotingProxy

REPORT_RECIPIENT_EMAIL = "procurations@actionpopulaire.fr"


def send_sms_message(*args, **kwargs):
    try:
        send_sms(*args, **kwargs)
    except SMSSendException:
        # TODO: do something more (ex. mark the phone number as invalid)
        pass


@emailing_task()
def send_voting_proxy_request_email(
    recipients, subject="", intro="", body="", link_label="", link_href="", ending=""
):
    bindings = {
        "MESSAGE_INTRO": intro,
        "MESSAGE_BODY": body,
        "MESSAGE_ENDING": ending,
        "LINK_LABEL": link_label,
        "LINK_HREF": link_href,
    }
    send_mosaico_email(
        code="VOTING_PROXY_REQUEST_EMAIL",
        subject=subject,
        from_email=settings.EMAIL_FROM,
        recipients=recipients,
        bindings=bindings,
    )


@post_save_task()
def send_voting_proxy_request_confirmation(voting_proxy_request_pks):
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        pk__in=voting_proxy_request_pks
    )
    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist()
    voting_proxy_request = voting_proxy_requests.first()

    # Send confirmation EMAIL
    send_voting_proxy_request_email.delay(
        [voting_proxy_request.email],
        subject="Votre demande de procuration de vote a bien été enregistrée",
        intro="Votre demande est enregistrée. Nous vous recontacterons dès qu'un-e volontaire sera disponible "
        "pour prendre votre procuration.",
    )

    # Send confirmation SMS
    message = (
        "Votre demande est enregistrée. Nous vous recontacterons dès qu'un-e volontaire sera disponible pour prendre "
        "votre procuration."
    )
    send_sms_message(
        message,
        voting_proxy_request.contact_phone,
    )


@post_save_task()
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
    link = shorten_url(link, secret=True)

    # Send proposition EMAIL
    send_voting_proxy_request_email.delay(
        [voting_proxy.email],
        subject="Proposition de prise de procuration de vote",
        intro=f"Quelqu'un près de chez vous a besoin d'une procuration {voting_dates} !",
        link_label="Confirmez votre disponibilité",
        link_href=link,
    )

    # Send proposition SMS
    message = (
        f"Quelqu'un près de chez vous a besoin d'une procuration {voting_dates} ! "
        f"Confirmez votre disponibilité : {link}"
    )
    send_sms_message(
        message,
        voting_proxy.contact_phone,
    )


@emailing_task()
def send_cancelled_request_to_voting_proxy(voting_proxy_request_pk, proxy_email):
    voting_proxy_request = VotingProxyRequest.objects.get(pk=voting_proxy_request_pk)
    voting_date = voting_proxy_request.voting_date.strftime("%d %B")
    send_voting_proxy_request_email.delay(
        [proxy_email],
        subject=f"Annulation de la procuration de vote du {voting_date}",
        intro=f"{voting_proxy_request.first_name}, pour qui vous aviez accepté de voter par procuration "
        f"le {voting_date}, a annulé sa demande. Nous vous proposerons d'autres demandes "
        f"près de chez vous dans les prochains jours, si besoin.",
    )


@emailing_task()
def send_cancelled_request_acceptation_to_request_owner(
    voting_proxy_request_pk, proxy_name
):
    voting_proxy_request = VotingProxyRequest.objects.get(pk=voting_proxy_request_pk)
    voting_date = voting_proxy_request.voting_date.strftime("%d %B")
    send_voting_proxy_request_email.delay(
        [voting_proxy_request.email],
        subject=f"Annulation de la procuration de vote du {voting_date}",
        intro=f"{proxy_name}, la personne qui avait accepté de voter pour vous par procuration le {voting_date}, "
        "vient de nous signaler qu'elle ne sera plus disponible. Nous sommes désolé du désagrément "
        "et essayerons de vous mettre en contact avec quelqu'un d'autre dans les plus brefs délais.",
    )


@emailing_task(post_save=True)
def send_voting_proxy_candidate_invitation_email(voting_proxy_canditate_emails):
    bindings = {
        "VOTING_PROXY_REQUEST_CREATION_LINK": front_url("new_voting_proxy"),
    }
    send_mosaico_email(
        code="VOTING_PROXY_CANDIDATE_INVITATION",
        subject="Êtes-vous disponible pour prendre une procuration ?",
        from_email=settings.EMAIL_FROM,
        recipients=voting_proxy_canditate_emails,
        bindings=bindings,
    )


@post_save_task()
def send_voting_proxy_request_accepted_text_messages(voting_proxy_request_pks):
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        pk__in=voting_proxy_request_pks
    ).order_by("voting_date")

    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist()

    voting_proxy_request = voting_proxy_requests.first()
    voting_dates = ", ".join(
        [vpr.voting_date.strftime("%d %B") for vpr in voting_proxy_requests]
    )
    if len(voting_proxy_request_pks) > 1:
        voting_dates = "les " + voting_dates
    else:
        voting_dates = "le " + voting_dates

    link = front_url(
        "voting_proxy_request_details",
        query={"vpr": ",".join([str(pk) for pk in voting_proxy_request_pks])},
    )
    link = shorten_url(link, secret=True)

    # Send acceptance EMAIL to request owner
    send_voting_proxy_request_email.delay(
        [voting_proxy_request.email],
        subject=f"{voting_proxy_request.proxy.first_name} s'est porté-e volontaire pour prendre votre procuration",
        intro=f"{voting_proxy_request.proxy.first_name} s'est porté-e volontaire pour voter "
        f"en votre nom {voting_dates} !",
        link_label="Voir la marche à suivre",
        link_href=link,
    )

    # Send acceptance SMS to request owner
    request_owner_message = (
        f"{to_7bit_string(voting_proxy_request.proxy.first_name)} s'est porté-e volontaire pour voter en votre nom "
        f"{voting_dates} ! {link}"
    )
    send_sms_message(
        request_owner_message,
        voting_proxy_request.contact_phone,
    )

    # Send acceptance EMAIL to voting proxy
    link = front_url(
        "accepted_voting_proxy_requests",
        kwargs={"pk": voting_proxy_request.proxy.pk},
    )
    link = shorten_url(link, secret=True)

    voting_proxy_message = format_html(
        f"Vous avez accepté de voter pour {voting_proxy_request.first_name} {voting_dates}."
        "\n\n"
        f"Nous vous préviendrons lorsque {voting_proxy_request.first_name} aura établi "
        f"la procuration de vote. Son numéro : {voting_proxy_request.contact_phone}"
    )
    send_voting_proxy_request_email.delay(
        [voting_proxy_request.proxy.email],
        subject="Procuration de vote acceptée",
        intro=voting_proxy_message,
        link_label="Voir mes procurations acceptées",
        link_href=link,
    )

    # Send acceptance SMS to voting proxy
    voting_proxy_message = (
        f"Vous avez accepté de voter pour {to_7bit_string(voting_proxy_request.first_name)} {voting_dates}. "
        f"Nous vous préviendrons lorsque {to_7bit_string(voting_proxy_request.first_name)} aura établi "
        f"la procuration de vote. Son numéro : {voting_proxy_request.contact_phone}"
    )
    send_sms_message(
        voting_proxy_message,
        voting_proxy_request.proxy.contact_phone,
    )


@post_save_task()
def send_voting_proxy_information_for_request(voting_proxy_request_pk):
    voting_proxy_request = VotingProxyRequest.objects.get(pk=voting_proxy_request_pk)
    # Send information EMAIL
    message = voting_proxy_request.get_voting_proxy_information(as_html=True)
    link = front_url(
        "voting_proxy_request_details",
        query={"vpr": voting_proxy_request_pk},
    )
    ending = format_html(
        """
        Une fois la demande en ligne validée :
        <ul>
            <li>
                Déplacez-vous au commissariat ou à la gendarmerie pour vérifier votre identité et valider la procuration
            </li>
            <li>Une fois la procuration validée, prévenez le ou la volontaire</li>
        </ul>
        <br />
        <em>
            Notre espace procurations étant ouvert à tout le monde, nous faisons tout le possible pour limiter au 
            maximum les abus. La plupart des nos volontaires sont des militant·es du mouvement et nous privilégions, 
            lors de la mise en relation, les personnes avec le plus d'ancienneté dans le mouvement.
            <br /><br />
            Pour réduire encore plus les risques d'utilisation malveillante, nous vous conseillons, si vous le pouvez, 
            d'échanger brièvement avec la personne volontaire ou de rechercher son nom et prénom sur internet pour vous 
            faire vous-même une idée.
            <br /><br />
            N'hésitez pas à nous signaler tout abus en nous écrivant à l'adresse : 
            <a href="mailto:procurations@actionpopulaire.fr">procurations@actionpopulaire.fr</a>.
        </em>
        """
    )
    send_voting_proxy_request_email.delay(
        [voting_proxy_request.email],
        subject="Les informations de votre procuration de vote",
        intro=format_html(
            "Retrouvez ci-dessous les informations pour établir votre procuration de vote sur <a href='{}'>"
            "le site du service public</a> (environ 3 min.) :",
            "https://www.maprocuration.gouv.fr/",
        ),
        body=message,
        ending=ending,
        link_label="Voir la page de la procuration",
        link_href=link,
    )
    # Send information SMS
    message = voting_proxy_request.get_voting_proxy_information()
    send_sms_message(
        message,
        voting_proxy_request.contact_phone,
    )


@post_save_task()
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
        f"Date(s)&nbsp;: <strong>{escape(voting_date_string)}</strong><br>"
        f"Volontaire&nbsp;: <strong>{escape(voting_proxy_request.first_name)} {escape(voting_proxy_request.last_name.upper())}</strong><br>"
        f"Circonscription&nbsp;: <strong>{escape(voting_proxy_request.commune.nom if voting_proxy_request.commune else voting_proxy_request.consulate.nom)}</strong><br>"
        f"Téléphone&nbsp;: <strong>{escape(voting_proxy_request.contact_phone)}</strong><br>"
    )
    if voting_proxy_request.polling_station_number:
        message += f"Bureau de vote&nbsp;: <strong>{escape(voting_proxy_request.polling_station_label)}</strong>"

    message = format_html(message)

    ending = format_html(
        f"""
        Une fois la procuration validée, vous n'aurez plus qu'à vous rendre dans le bureau de la personne le jour du 
        vote avec votre pièce d'identité.
        <br />
        <br />
        Vous pouvez vérifier la bonne validation de la procuration à votre nom en vous connectant sur 
        <a href='https://www.service-public.fr/particuliers/vosdroits/demarches-et-outils/ISE'>le site du service 
        public</a> (la procuration peut prendre un peu de temps à apparaître).
        <br />
        <br />
        Si vous le pouvez, nous vous conseillons de demander à votre mandant de vous envoyer une photo/copie du 
        récépissé de validation de sa demande par les autorités, qui peut être utile en cas de mauvaise transmission 
        de celle-ci au bureau de vote.
        """
    )

    # Send confirmation EMAIL
    send_voting_proxy_request_email.delay(
        [voting_proxy_request.proxy.email],
        subject="Procuration de vote confirmée",
        intro=f"{voting_proxy_request.first_name} a confirmé l'établissement de sa procuration de vote :",
        body=message,
        ending=ending,
    )

    message = (
        f"Procuration de vote établie ({voting_date_string}) :"
        f" {to_7bit_string(voting_proxy_request.first_name)} {to_7bit_string(voting_proxy_request.last_name.upper())}"
        f" - {to_7bit_string(voting_proxy_request.commune.nom if voting_proxy_request.commune else voting_proxy_request.consulate.nom)}"
        f" - tél. {voting_proxy_request.contact_phone}"
    )
    if voting_proxy_request.polling_station_number:
        message += f" - bureau de vote {to_7bit_string(voting_proxy_request.polling_station_label)}"

    # Send confirmation SMS
    send_sms_message(
        message,
        voting_proxy_request.proxy.contact_phone,
    )


@post_save_task()
def send_voting_proxy_request_confirmation_reminder(voting_proxy_request_pks):
    voting_proxy_requests = VotingProxyRequest.objects.filter(
        pk__in=voting_proxy_request_pks
    ).order_by("voting_date")

    if not voting_proxy_requests.exists():
        raise VotingProxyRequest.DoesNotExist()

    voting_proxy_request = voting_proxy_requests.first()

    link = front_url(
        "voting_proxy_request_details",
        query={"vpr": ",".join([str(pk) for pk in voting_proxy_request_pks])},
    )
    link = shorten_url(link, secret=True)

    ending = format_html(
        "Pour éviter des problèmes le jour du scrutin, nous conseillons aux personnes donnant procuration de vote de se "
        "déplacer au commissariat, à la gendarmerie ou au consulat pour vérifier leur identité et valider la "
        "procuration le plus tôt possible et <strong>avant le 27 juin pour le premier tour et le 4 juillet pour le "
        "second</strong>."
    )

    # Send confirmation reminder EMAIL to request owner
    send_voting_proxy_request_email.delay(
        [voting_proxy_request.email],
        subject="Confirmation de votre procuration de vote",
        intro=f"Envoyez une confirmation à {voting_proxy_request.proxy.first_name} que votre procuration de vote "
        f"a été établie à son nom, validée par les autorités et que tout est prêt pour le jour du scrutin.",
        link_label="Je confirme",
        link_href=link,
        ending=ending,
    )

    # Send confirmation reminder SMS to request owner
    request_owner_message = (
        f"Envoyez une confirmation à {to_7bit_string(voting_proxy_request.proxy.first_name)} que votre "
        f"procuration de vote a été établie à son nom et que tout est prêt pour le jour du scrutin. {link}"
    )
    send_sms_message(
        request_owner_message,
        voting_proxy_request.contact_phone,
    )

    link = front_url(
        "accepted_voting_proxy_requests",
        kwargs={"pk": voting_proxy_request.proxy.pk},
    )
    link = shorten_url(link, secret=True)

    # Send confirmation reminder EMAIL to voting proxy
    send_voting_proxy_request_email.delay(
        [voting_proxy_request.proxy.email],
        subject="Procuration de vote",
        intro=(
            f"{voting_proxy_request.first_name} n'a pas encore confirmé l'établissement de la procuration de vote. "
            f"Assurez-vous que vous pourrez voter en son nom ! "
            f"Son numéro : {voting_proxy_request.contact_phone}"
        ),
        link_label="Voir mes procurations acceptées",
        link_href=link,
        ending=ending,
    )

    # Send confirmation reminder SMS to voting proxy
    proxy_message = (
        f"{to_7bit_string(voting_proxy_request.first_name)} n'a pas encore confirmé l'établissement de la "
        f"procuration de vote. Assurez-vous que vous pourrez voter en son nom ! "
        f"Son numéro : {voting_proxy_request.contact_phone} - {link}"
    )
    send_sms_message(
        proxy_message,
        voting_proxy_request.proxy.contact_phone,
    )


@emailing_task()
def send_matching_report_email(data):
    subject = f"Rapport du script des procurations - {data['datetime']}"
    if data["dry_run"]:
        subject = "[DRY-RUN] " + subject

    body = f"""
Bonjour,

==============================================================
PROCURATIONS - RAPPORT DE SCRIPT
{data["datetime"]}

- {data["pending_request_count"]} demande(s) de procuration en attente
- {data["matched_request_count"]} demande(s) de procuration proposée(s) à un·e volontaire
- {len(data["invitations"])} invitation(s) envoyée(s) à des volontaires potentiels
==============================================================

Cordialement.

L'équipe d'Action populaire.
    """
    connection = get_connection()
    with connection:
        email = EmailMultiAlternatives(
            connection=connection,
            from_email="robot@actionpopulaire.fr",
            subject=subject,
            to=(REPORT_RECIPIENT_EMAIL,),
            body=body,
        )

        for filename in ("pending_requests", "matched_proxies", "invitations"):
            content = json.dumps(data[filename])
            attachment = MIMEText(content.rstrip("\n"), "plain", "utf-8")
            attachment.add_header("Content-Type", "application/json")
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=f"{filename}{'.dry' if data['dry_run'] else ''}.json",
            )
            email.attach(attachment)

        email.send()
