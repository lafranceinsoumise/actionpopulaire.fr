from typing import List, Tuple

import reversion
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from agir.lib.models import TimeStampedModel
from agir.people.models import Person
from .commentaires import Commentaire
from .common import ModeleGestionMixin, NumeroManager
from .utils import NiveauTodo, Todo, no_todos, Transition
from ..typologies import TypeProjet, NiveauAcces, TypeDepense, TypeDocument

__all__ = ("Projet", "Participation", "ProjetMilitant")


class ProjetManager(NumeroManager):
    def from_event(self, event, user):
        try:
            projet = self.get(event=event)
        except self.model.DoesNotExist:
            with reversion.create_revision():
                reversion.set_comment("Création à partir d'un événement utilisateur")
                reversion.set_user(user)
                titre = event.name if len(event.name) < 40 else f"{event.name[:39]}…"
                return self.create(
                    event=event,
                    etat=Projet.Etat.CREE_PLATEFORME,
                    titre=titre,
                    type=event.subtype.related_project_type or TypeProjet.ACTIONS,
                    description="Ce projet a été généré automatiquement à partir d'un événement créé par un "
                    "utilisateur d'Action Populaire.",
                    origine=Projet.Origin.UTILISATEUR,
                )
        else:
            if projet.type != event.subtype.related_project_type:
                with reversion.create_revision():
                    reversion.set_comment(
                        "Changement du type d'événement associé par l'utilisateur"
                    )
                    reversion.set_user(user)
                    projet.type = (
                        event.subtype.related_project_type or TypeProjet.ACTIONS
                    )
                    projet.save(update_fields=["type"])

            return projet


@reversion.register(follow=["participations"])
class Projet(ModeleGestionMixin, TimeStampedModel):

    """Le projet regroupe ensemble des dépenses liées entre elles

    Un projet peut correspondre à un événement, ou à un type de de dépense précis.
    (par exemple « organisation du meeting du 16 janvier » ou « paiement salaire mars »)
    """

    objects = ProjetManager()

    class Etat(models.TextChoices):
        CREE_PLATEFORME = "DFI", "Créé par un·e militant·e"
        REFUSE = "REF", "Refusé"
        EN_CONSTITUTION = "ECO", "En cours de constitution"
        FINALISE = "FIN", "Finalisé par le secrétariat"
        RENVOI = "REN", "Renvoyé par l'équipe financière"
        CLOTURE = "CLO", "Clôturé"

    ETATS_FINAUX = (Etat.REFUSE, Etat.CLOTURE)

    TRANSITIONS = {
        Etat.CREE_PLATEFORME: [
            Transition(
                nom="Accepter le projet",
                vers=Etat.EN_CONSTITUTION,
                permissions=["gestion.gerer_projet"],
                class_name="success",
            ),
            Transition(
                nom="Refuser le projet",
                vers=Etat.REFUSE,
                permissions=["gestion.gerer_projet"],
                class_name="failure",
            ),
        ],
        Etat.EN_CONSTITUTION: [
            Transition(
                nom="Finaliser le projet",
                vers=Etat.FINALISE,
                condition=no_todos,
                permissions=["gestion.gerer_projet"],
                class_name="success",
            )
        ],
        Etat.FINALISE: [
            Transition(
                nom="Renvoyer le projet",
                vers=Etat.RENVOI,
                permissions=["gestion.controler_projet"],
                class_name="failure",
            ),
            Transition(
                nom="Cloturer le projet",
                vers=Etat.CLOTURE,
                condition=no_todos,
                permissions=["gestion.controler_projet"],
                class_name="success",
            ),
        ],
    }

    class Origin(models.TextChoices):
        ADMINISTRATION = "A", "Créé par les équipes de campagne"
        UTILISATEUR = "U", "Créé par un·e militant·e sur Action Populaire"
        REUNION_PUBLIQUE = "R", "Réunion publique suite à demande"

    SHORT_ORIGIN = {
        Origin.ADMINISTRATION: "campagne",
        Origin.UTILISATEUR: "militant",
        Origin.REUNION_PUBLIQUE: "réunion publique",
    }

    titre = models.CharField(verbose_name="Titre du projet", max_length=200)
    type = models.CharField(
        verbose_name="Type de projet", choices=TypeProjet.choices, max_length=10
    )
    origine = models.CharField(
        verbose_name="Origine du projet",
        max_length=1,
        choices=Origin.choices,
        editable=False,
        default=Origin.ADMINISTRATION,
    )

    etat = models.CharField(
        verbose_name="État",
        max_length=3,
        choices=Etat.choices,
        blank=False,
        default=Etat.CREE_PLATEFORME,
    )
    description = models.TextField(verbose_name="Description du projet", null=True)
    event = models.ForeignKey(
        to="events.Event",
        verbose_name="Événement sur la plateforme",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    date_evenement = models.DateField(
        "date de l'événement",
        help_text="À utiliser s'il n'y a pas d'événement associé, ou si il faut utiliser une autre date que celle de "
        "l'événement",
        null=True,
        blank=True,
    )

    code_insee = models.CharField(
        "code INSEE commune",
        max_length=5,
        help_text="À utiliser s'il n'y a pas d'événement associé, ou si il faut utiliser un autre lieu que celui de l'événement",
        blank=True,
        validators=[RegexValidator(regex=r"^\d{5}$")],
    )

    niveau_acces = models.CharField(
        verbose_name="Niveau d'accès",
        max_length=1,
        choices=NiveauAcces.choices,
        blank=False,
        default=NiveauAcces.SANS_RESTRICTION,
    )

    documents = models.ManyToManyField(
        to="Document", related_name="projets", related_query_name="projet"
    )

    # Ce champ JSON est utilisé pour sauvegarder un certain nombre de réglages du projet.
    # (ci-dessous, une clé "a.b" désigne la clé "b" de l'objet à la clé "a" de l'objet détails)
    # Pour le moment, les clés suivantes sont définies :
    # - la clé "documents.absents" est une liste de type de documents normalement requis pour ce type de projets, mais
    #   indiqué comme explicitement absent sur le projet concerné.
    details = models.JSONField("Détails", default=dict)

    def todos(self):
        return todos(self)

    @property
    def transitions(self):
        # noinspection PyTypeChecker
        return self.TRANSITIONS.get(self.etat, [])

    def __str__(self):
        if len(self.titre) < 60:
            titre = self.titre
        else:
            titre = f"{self.titre[:60]}…"

        # noinspection PyTypeChecker
        return f"{titre} ({self.SHORT_ORIGIN[self.origine]})"

    search_config = (
        ("numero", "B"),
        ("titre", "A"),
        ("description", "C"),
        ("event__name", "B"),
        ("event__description", "C"),
        ("event__location_name", "C"),
        ("event__location_city", "C"),
        ("event__contact_name", "D"),
        ("event__contact_phone", "D"),
    )

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"


@reversion.register()
class Participation(TimeStampedModel):
    """Ce modèle associe des personnes à des projets, et indique leur rôle sur le projet"""

    class Role(models.TextChoices):
        CANDIDAT = "CAN", "Candidat"
        ORATEUR = "ORA", "Orateur"
        ORGANISATION = (
            "ORG",
            "Organisation",
        )
        GESTION = "GES", "Gestion de projet"

    projet = models.ForeignKey(
        to=Projet,
        verbose_name="Projet",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="participations",
        related_query_name="participation",
    )
    person = models.ForeignKey(
        to="people.Person",
        verbose_name="Personne",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name="+",
        related_query_name="participation",
    )
    role = models.CharField(
        verbose_name="Rôle sur ce projet",
        max_length=3,
        choices=Role.choices,
    )

    precisions = models.TextField(verbose_name="Précisions", blank=True)

    class Meta:
        verbose_name = "participation à un projet"
        verbose_name_plural = "participations à des projets"
        unique_together = ("projet", "person", "role")


def verifier_transports(projet: Projet):
    intervenants = projet.participations.values_list("person_id", flat=True)

    transportes = Person.objects.filter(
        depense__projet_id=projet.pk, depense__type__startswith=TypeDepense.TRANSPORTS
    ).values_list("id", flat=True)

    return not intervenants.difference(transportes).exists()


def verifier_hebergement(projet: Projet):
    intervenants = projet.participations.values_list(
        "person_id", flat=True
    ).difference()

    heberges = Person.objects.filter(
        depense__projet_id=projet.pk,
        depense__type__startswith=TypeDepense.FRAIS_RECEPTION_HEBERGEMENT,
    ).values_list("id", flat=True)

    return not intervenants.difference(heberges).exists()


TYPE_TODOS = {
    TypeProjet.CONFERENCE_PRESSE: [
        Todo(
            models.Q(
                participation__role__in=[
                    Participation.Role.ORATEUR,
                    Participation.Role.CANDIDAT,
                ]
            ),
            "La conférence de presse doit identifier les intervenants, orateurs ou candidats.",
            NiveauTodo.IMPERATIF,
        )
    ],
    TypeProjet.REUNION_PUBLIQUE: [
        Todo(
            models.Q(documents__type=TypeDocument.PHOTOGRAPHIE),
            "Des photos de la réunion publique doivent être ajoutées après le déroulement de l'événement.",
            NiveauTodo.AVERTISSEMENT,
        ),
        Todo(
            verifier_transports,
            "La réunion publique doit inclure les dépenses de transport pour chacun des intervenants listés.",
            NiveauTodo.IMPERATIF,
        ),
        Todo(
            verifier_hebergement,
            "La réunion publique doit inclure les dépenses d'hébergement et de restauration pour chacun des intervenants listés.",
            NiveauTodo.IMPERATIF,
        ),
    ],
    TypeProjet.REUNION_PUBLIQUE_ORATEUR: [
        Todo(
            models.Q(participation__role__in=[Participation.Role.ORATEUR]),
            "La réunion publique doit identifier les orateurs qui s'y sont rendus.",
            NiveauTodo.IMPERATIF,
        )
    ],
    TypeProjet.REUNION_PUBLIQUE_CANDIDAT: [
        Todo(
            models.Q(participation__role__in=[Participation.Role.CANDIDAT]),
            "La réunion publique doit identifier les candidats et orateurs qui y sont intervenus.",
            NiveauTodo.IMPERATIF,
        )
    ],
}


class ProjetMilitantManager(ProjetManager):
    def get_queryset(self):
        return super().get_queryset().filter(origine=Projet.Origin.UTILISATEUR)


class ProjetMilitant(Projet):
    objects = ProjetMilitantManager()

    class Meta:
        proxy = True


def todos(projet: Projet):
    todos: List[Tuple[str, List[Tuple[str, NiveauTodo]]]] = []

    generic_todos = []
    if projet.event is None:
        generic_todos.append(
            (
                "Commencez par sélectionner l'événement concerné par ce projet.",
                NiveauTodo.SUGGESTION,
            )
        )

    if generic_todos:
        todos.append(("Obligations générales", generic_todos))

    type_todos = []
    for type, conditions in TYPE_TODOS.items():
        if projet.type.startswith(type):
            for cond in conditions:
                if not cond.check(projet):
                    type_todos.append((cond.message_erreur, cond.niveau_erreur))

    if type_todos:
        todos.append(("Obligations pour ce type de projet", type_todos))

    depense_todos = []
    com_todo_annote = models.Exists(
        Commentaire.objects.filter(projet__id=models.OuterRef("id"))
    )

    for d in projet.depenses.annotate(avec_com_todos=com_todo_annote):
        if d.todos() or d.avec_com_todos:
            depense_todos.append(
                (
                    format_html(
                        'La dépense <a href="{link}">{depense}</a> a une todoliste remplie !',
                        link=reverse("admin:gestion_depense_change", args=(d.id,)),
                        depense=f"{d.titre} ({d.numero})",
                    ),
                    NiveauTodo.IMPERATIF,
                )
            )

    if depense_todos:
        todos.append(("Tâches liées aux dépenses associées à ce projet", depense_todos))

    return todos
