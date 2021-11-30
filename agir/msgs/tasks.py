from django.urls import reverse
from django.utils.html import format_html

from agir.msgs.models import UserReport
from django.core.mail import get_connection, EmailMultiAlternatives

from agir.lib.celery import emailing_task, post_save_task


@emailing_task
@post_save_task
def send_message_report_email(report_pk):
    report = UserReport.objects.get(pk=report_pk)
    connection = get_connection()
    subject = f"“🤖” Signalement #{report_pk}"
    body_text = f"""
Bonjour.

Un nouveau signalement a été reçu [n°{report_pk}] 
de la part de {str(report.reporter)}.

============================================================
 {report.reported_object._meta.model._meta.verbose_name.title().upper()}
 de {str(report.reported_object.author)}
 ID : {report.reported_object.pk} 
=============================================================

Cordialement.

L'équipe d'Action populaire (“🤖”).
    """

    with connection:
        email = EmailMultiAlternatives(
            connection=connection,
            from_email="robot@actionpopulaire.fr",
            subject=subject,
            to=["groupes@actionpopulaire.fr"],
            body=body_text,
        )

        email.send()
