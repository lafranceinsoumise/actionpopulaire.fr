from typing import List, Tuple

import reversion
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from agir.lib.models import TimeStampedModel
from agir.people.models import Person
from .commentaires import Commentaire
from .common import ModeleGestionMixin
from ..actions import Todo, NiveauTodo, Transition, no_todos
from ..typologies import TypeProjet, NiveauAcces, TypeDepense, TypeDocument

__all__ = (
    "Projet",
    "Participation",
)


@reversion.register(follow=["participations"])
class Projet(ModeleGestionMixin, TimeStampedModel):

    """Le projet regroupe ensemble des dépenses liées entre elles

    Un projet peut correspondre à un événement, ou à un type de de dépense précis.
    (par exemple « organisation du meeting du 16 janvier » ou « paiement salaire mars »)
    """

    class Etat(models.TextChoices):
        DEMANDE_FINANCEMENT = "DFI", "Demande de financement"
        REFUSE = "REF", "Refusé"
        EN_CONSTITUTION = "ECO", "En cours de constitution"
        FINALISE = "FIN", "Finalisé par le secrétariat"
        RENVOI = "REN", "Renvoyé par l'équipe financière"
        CLOTURE = "CLO", "Clôturé"

    TRANSITIONS = {
        Etat.DEMANDE_FINANCEMENT: [
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

    titre = models.CharField(verbose_name="Titre du projet", max_length=40)
    type = models.CharField(
        verbose_name="Type de projet", choices=TypeProjet.choices, max_length=10
    )
    etat = models.CharField(
        verbose_name="Statut",
        max_length=3,
        choices=Etat.choices,
        blank=False,
        default=Etat.DEMANDE_FINANCEMENT,
    )
    description = models.TextField(verbose_name="Description du projet", null=True)
    event = models.ForeignKey(
        to="events.Event",
        verbose_name="Événement sur la plateforme",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    niveau_acces = models.CharField(
        verbose_name="Niveau d'accès",
        max_length=1,
        choices=NiveauAcces.choices,
        blank=False,
        default=NiveauAcces.SANS_RESTRICTION,
    )

    details = models.JSONField("Détails", default=dict)

    documents = models.ManyToManyField(
        to="Document", related_name="projets", related_query_name="projet"
    )

    def todos(self):
        return todos(self)

    @property
    def transitions(self):
        return self.TRANSITIONS[self.etat]

    search_config = (
        ("numero", "B"),
        ("titre", "A"),
        ("description", "C"),
        ("event__name", "B"),
        ("event__description", "B"),
    )

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"


@reversion.register()
class Participation(TimeStampedModel):
    """Ce modèle associe des personnes à des projets, et indique leur rôle sur le projet
    """

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
        verbose_name="Rôle sur ce projet", max_length=3, choices=Role.choices,
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
