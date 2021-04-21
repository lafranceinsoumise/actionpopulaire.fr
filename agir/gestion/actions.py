import dateutil
from django.utils import timezone
from django.utils.html import format_html_join

from agir.people.models import Person


def ajouter_commentaire(instance, texte, statut, auteur):
    instance.commentaires.append(
        {
            "auteur": str(auteur.id),
            "date": timezone.now().isoformat(),
            "message": texte,
            "statut": statut,
            "cacher": False,
        }
    )


def afficher_commentaires(instance, template=None):
    if template is None:
        template = "<div><strong>{auteur} — {date}</strong><p>{message}</p></div>"

    return format_html_join(
        "",
        template,
        (
            {
                "auteur": Person.objects.filter(id=com["auteur"]).first(),
                "date": dateutil.parser.parse(com["date"]).strftime(
                    "%H:%M le %d/%m/%Y"
                ),
                "message": com["message"],
            }
            for com in instance.commentaires
        ),
    )
