from agir.gestion.models import Commentaire
from agir.people.models import Person


def ajouter_commentaire(instance, texte, type, auteur: Person):
    c = Commentaire.objects.create(
        auteur=auteur, auteur_nom=auteur.get_full_name(), texte=texte, type=type
    )
    instance.commentaires.add(c)


def nombre_commentaires_a_faire(instance):
    return instance.commentaires.filter(type=Commentaire.Type.TODO).count()
