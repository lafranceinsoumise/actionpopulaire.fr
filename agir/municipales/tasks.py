from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template

from agir.lib.celery import emailing_task
from agir.municipales.models import CommunePage
from agir.people.models import Person


@emailing_task(post_save=True)
def notify_commune_changed(commune_id, person_id, changed_data):
    commune = CommunePage.objects.get(id=commune_id)
    nom_commune = f"{commune.name} ({commune.code_departement})"

    try:
        person = Person.objects.get(id=person_id)
        author = f"{person.get_full_name()} <{person.email}>"
    except Person.DoesNotExist:
        author = "<compte supprimé>"

    template = get_template("municipales/commune_change_notification.txt")
    context = {"author": author, "commune": nom_commune, "changed_data": changed_data}
    body = template.render(context)

    message = EmailMessage(
        subject=f"Modification commune {nom_commune}",
        body=body,
        from_email=settings.EMAIL_FROM,
        to=["groupes-action@lafranceinsoumise.fr"],
    )
    message.send()


@emailing_task(post_save=True)
def send_procuration_email(commune_id, nom_complet, email, phone, bureau, autres):
    commune = CommunePage.objects.get(id=commune_id)
    if commune.contact_email:
        personnel = False
        recipients = [commune.contact_email]
    else:
        recipients = [p.email for p in commune.chefs_file.all()]
        personnel = True

    if not recipients:
        recipients = ["groupes-action@lafranceinsoumise.fr"]

    template = get_template("municipales/procuration_notification.txt")
    context = {
        "nom_complet": nom_complet,
        "email": email,
        "phone": phone,
        "bureau": bureau,
        "autres": autres,
        "personnel": personnel,
    }
    body = template.render(context)

    message = EmailMessage(
        subject=f"Demande de procuration - {nom_complet}",
        body=body,
        from_email=settings.EMAIL_FROM,
        to=recipients,
    )
    message.send()
