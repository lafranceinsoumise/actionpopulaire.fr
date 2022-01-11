import re
from typing import List

import reversion
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from agir.authentication.models import Role
from agir.gestion.actions import Todo, NiveauTodo, Transition, no_todos
from agir.gestion.models.common import ModeleGestionMixin, NumeroQueryset
from agir.gestion.typologies import TypeDepense, NiveauAcces, TypeDocument
from agir.lib.model_fields import IBANField
from agir.lib.models import TimeStampedModel, LocationMixin

__all__ = ("Depense", "Reglement", "Fournisseur")


def engagement_autorise(depense: "Depense", role):
    compte = depense.compte
    if role.has_perm("gestion.engager_depense") or role.has_perm(
        "gestion.engager_depense", obj=compte
    ):
        return True
    elif (
        role.has_perm("gestion.gerer_depense")
        or role.has_perm("gestion.gerer_depense", obj=compte)
        and verifier_plafond_engagement(depense)
    ):
        return True
    return False


def engager_depense(depense: "Depense"):
    if depense.date_depense is None:
        depense.date_depense = timezone.now()


class DepenseQuerySet(NumeroQueryset):
    def annoter_reglement(self):
        return self.annotate(
            prevu=models.Sum("reglement__montant"),
            regle=models.Sum(
                Reglement.objects.filter(
                    statut__in=[Reglement.Statut.REGLE, Reglement.Statut.RAPPROCHE],
                    depense_id=models.OuterRef("id"),
                ).values("montant")
            ),
        )


@reversion.register()
class Depense(ModeleGestionMixin, TimeStampedModel):
    """Une dépense correspond à un paiement réalisé en lien avec une facture"""

    objects = DepenseQuerySet.as_manager()

    class Etat(models.TextChoices):
        REFUS = "R", "Dossier refusé"
        ATTENTE_VALIDATION = "V", "En attente de validation d'opportunité"
        ATTENTE_ENGAGEMENT = "A", "En attente de l'engagement de la dépense"
        CONSTITUTION = "C", "Constitution du dossier"
        COMPLET = "O", "Dossier complété"
        CLOTURE = "L", "Dossier clôturé"

    TRANSITIONS = {
        Etat.ATTENTE_VALIDATION: [
            Transition(
                nom="Valider la dépense",
                vers=Etat.ATTENTE_ENGAGEMENT,
                class_name="success",
                permissions=["gestion.gerer_depense"],
            ),
            Transition(
                nom="Refuser la dépense",
                vers=Etat.REFUS,
                class_name="failure",
                permissions=["gestion.gerer_depense"],
            ),
        ],
        Etat.ATTENTE_ENGAGEMENT: [
            Transition(
                nom="Engager la dépense",
                vers=Etat.CONSTITUTION,
                class_name="success",
                condition=engagement_autorise,
                effect=engager_depense,
            ),
            Transition(
                nom="Refuser l'engagement de la dépense",
                vers=Etat.REFUS,
                class_name="failure",
                permissions=["gestion.engager_depense", "gestion.gerer_depense"],
            ),
        ],
        Etat.CONSTITUTION: [
            Transition(
                nom="Compléter et transmettre le dossier",
                vers=Etat.COMPLET,
                condition=no_todos,
                class_name="success",
                permissions=["gestion.gerer_depense"],
            ),
        ],
        Etat.COMPLET: [
            Transition(
                nom="Renvoyer le dossier pour précisions",
                vers=Etat.CONSTITUTION,
                permissions=["gestion.responsable_compte"],
                class_name="failure",
            ),
            Transition(
                nom="Clôturer le dossier",
                vers=Etat.CLOTURE,
                condition=no_todos,
                permissions=["gestion.responsable_compte"],
                class_name="success",
            ),
        ],
    }

    titre = models.CharField(
        verbose_name="Titre de la dépense",
        help_text="Une description sommaire de la nature de la dépense",
        blank=False,
        max_length=100,
    )

    description = models.TextField(
        verbose_name="Description",
        help_text="La description doit permettre de pouvoir identifier de façon non ambigue la dépense et sa nature dans le cas où le titre ne suffit pas.",
        blank=True,
    )

    compte = models.ForeignKey(
        to="Compte",
        null=False,
        related_name="depenses",
        related_query_name="depense",
        help_text="Le compte dont fait partie cette dépense.",
        on_delete=models.PROTECT,
    )

    projet = models.ForeignKey(
        to="Projet",
        null=True,
        blank=True,
        related_name="depenses",
        related_query_name="depense",
        help_text="Le projet éventuel auquel est rattaché cette dépense.",
        on_delete=models.SET_NULL,
    )

    type = models.CharField(
        "Type de dépense", max_length=5, choices=TypeDepense.choices
    )

    montant = models.DecimalField(
        verbose_name="Montant de la dépense",
        decimal_places=2,
        null=False,
        max_digits=10,
    )

    etat = models.CharField(
        verbose_name="État de ce dossier de dépense",
        max_length=1,
        choices=Etat.choices,
        default=Etat.ATTENTE_VALIDATION,
        null=False,
    )

    quantite = models.IntegerField(
        verbose_name="Quantité",
        null=True,
        blank=True,
        help_text="Lorsque la dépense correspond à l'achat de matériel, indiquez ici la quantité achetée.",
    )

    nature = models.CharField(
        verbose_name="Nature",
        max_length=200,
        blank=True,
        help_text="La nature du bien acheté, à remplir simultanément avec le champ quantité si applicable.",
    )

    date_debut = models.DateField(
        "Date de début",
        blank=True,
        null=True,
        help_text="Premier jour d'utilisation du matériel, premier jour de l'opération correspondante.",
    )

    date_fin = models.DateField(
        "Date de fin",
        blank=True,
        null=True,
        help_text="Dernier jour d'utilisation du matériel, dernier jour de l'opération correspondante.",
    )

    date_depense = models.DateField(
        "Date d'engagement de la dépense",
        blank=True,
        null=True,
        help_text="Date à laquelle la dépense a été engagée (généralement l'acceptation du contrat)",
    )

    documents = models.ManyToManyField(
        to="Document",
        related_name="depenses",
        related_query_name="depense",
    )

    fournisseur = models.ForeignKey(
        "Fournisseur", null=True, blank=True, on_delete=models.SET_NULL
    )

    beneficiaires = models.ManyToManyField(
        to="people.Person",
        verbose_name="Bénéficiaires de la dépense",
        related_name="depenses",
        related_query_name="depense",
        blank=True,
    )

    depenses_refacturees = models.ManyToManyField(
        to="Depense",
        verbose_name="Dépenses à refacturer",
        related_name="refacturations",
        related_query_name="refacturation",
        blank=True,
        help_text="Toutes les dépenses concernées par cette refacturation.",
    )

    niveau_acces = models.CharField(
        verbose_name="Niveau d'accès",
        max_length=1,
        choices=NiveauAcces.choices,
        blank=False,
        default=NiveauAcces.SANS_RESTRICTION,
    )

    def clean(self, exclude=None):
        errors = {}

        try:
            super().clean()
        except ValidationError as e:
            e.update_error_dict(errors)

        if errors:
            raise ValidationError(errors)

    @property
    def devis_present(self):
        return self.documents.filter(type=TypeDocument.DEVIS).exists()

    @property
    def facture_presente(self):
        return self.documents.filter(type=TypeDocument.FACTURE).exists()

    @property
    def montant_restant(self):
        return self.montant - (
            self.reglements.aggregate(paye=models.Sum("montant"))["paye"] or 0
        )

    @property
    def depense_reglee(self):
        return (
            self.reglements.filter(statut=Reglement.Statut.REGLE).aggregate(
                paye=models.Sum("montant")
            )["paye"]
            == self.montant
        )

    @property
    def finalise(self):
        return self.etat in [self.Etat.COMPLET, self.Etat.CLOTURE]

    def todos(self):
        return todos(self)

    @property
    def transitions(self) -> List[Transition["Depense", Etat]]:
        return self.TRANSITIONS.get(self.Etat(self.etat), [])

    search_config = (
        ("numero", "B"),
        ("titre", "A"),
        ("description", "B"),
        ("nature", "C"),
    )

    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"


@reversion.register(follow=["depense"])
class Reglement(TimeStampedModel):
    class Statut(models.TextChoices):
        ATTENTE = "C", "En cours"
        REGLE = "R", "Réglé"
        RAPPROCHE = "P", "Rapproché"

    class Mode(models.TextChoices):
        VIREMENT = "V", "Par virement"
        PRELEV = "P", "Par prélèvement"
        CHEQUE = "C", "Par chèque"
        CARTE = "A", "Par carte bancaire"
        CASH = "S", "En espèces"

    depense = models.ForeignKey(
        to="Depense",
        verbose_name="Dépense concernée",
        related_name="reglements",
        related_query_name="reglement",
        on_delete=models.PROTECT,
    )

    intitule = models.CharField(
        verbose_name="Intitulé du réglement", max_length=200, blank=False
    )

    mode = models.CharField(
        verbose_name="Mode de réglement",
        max_length=1,
        choices=Mode.choices,
        blank=False,
    )

    montant = models.DecimalField(
        verbose_name="Montant du règlement",
        decimal_places=2,
        null=False,
        max_digits=10,
    )
    date = models.DateField(
        verbose_name="Date du règlement",
        blank=False,
        null=False,
        default=timezone.now,
    )

    date_releve = models.DateField(
        verbose_name="Date dans le relevé bancaire",
        blank=True,
        null=True,
    )

    preuve = models.ForeignKey(
        to="Document",
        verbose_name="Preuve de paiement",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    statut = models.CharField(
        max_length=1, blank=False, choices=Statut.choices, default=Statut.ATTENTE
    )

    # lien vers le fournisseur
    fournisseur = models.ForeignKey(
        to="Fournisseur",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # informations fournisseurs
    nom_fournisseur = models.CharField(
        verbose_name="Nom du fournisseur", blank=False, max_length=100
    )

    iban_fournisseur = IBANField(verbose_name="IBAN du fournisseur", blank=True)

    contact_phone_fournisseur = PhoneNumberField(
        verbose_name="Numéro de téléphone", blank=True
    )
    contact_email_fournisseur = models.EmailField(
        verbose_name="Adresse email", blank=True
    )

    location_address1_fournisseur = models.CharField(
        "adresse (1ère ligne)", max_length=100, blank=True
    )
    location_address2_fournisseur = models.CharField(
        "adresse (2ère ligne)", max_length=100, blank=True
    )
    location_city_fournisseur = models.CharField("ville", max_length=100, blank=False)
    location_zip_fournisseur = models.CharField(
        "code postal", max_length=20, blank=False
    )
    location_country_fournisseur = CountryField(
        "pays", blank_label="(sélectionner un pays)", default="FR", blank=False
    )

    search_config = (
        ("numero", "B"),
        ("titre", "A"),
        ("description", "B"),
    )

    class Meta:
        verbose_name = "règlement"
        ordering = ("date",)


@reversion.register()
class Fournisseur(LocationMixin, TimeStampedModel):
    """Ce modèle permet d'enregistrer des fournisseurs récurrents.

    Un fournisseur peut posséder une adresse, un IBAN pour réaliser des virements,
    et des informations de contact.
    """

    nom = models.CharField(
        verbose_name="Nom du fournisseur", blank=False, max_length=100
    )
    description = models.TextField(verbose_name="Description", blank=True)

    iban = IBANField(verbose_name="IBAN du fournisseur", blank=True)

    contact_phone = PhoneNumberField(verbose_name="Numéro de téléphone", blank=True)
    contact_email = models.EmailField(verbose_name="Adresse email", blank=True)

    def __str__(self):
        return self.nom


CONDITIONS = {
    TypeDepense.FOURNITURE_MARCHANDISES: (
        Todo(
            Q(documents__type=TypeDocument.PHOTOGRAPHIE),
            "Vous devez joindre une photographie de la marchandise pour justifier cette dépense.",
            NiveauTodo.IMPERATIF,
        ),
    ),
    TypeDepense.FRAIS_RECEPTION_HEBERGEMENT: (
        Todo(
            Q(beneficiaires__isnull=False),
            "Les dépenses de réception ou d'hébergement doivent identifier les personnes bénéficiaires de la dépense.",
            NiveauTodo.IMPERATIF,
        ),
    ),
    TypeDepense.GRAPHISME_MAQUETTAGE: (
        Todo(
            Q(documents__type=TypeDocument.EXEMPLAIRE),
            "Vous devez joindre un exemplaire numérique du graphisme ou du maquettage realisé.",
            NiveauTodo.IMPERATIF,
        ),
    ),
}


TYPE_DERNIERE_PARTIE_RE = re.compile(r"(?:^|-)[^-]+$")


def verifier_plafond_engagement(depense):
    compte = depense.compte

    # Il faut prendre en compte la nature hiérarchique des types
    # Pour cela on boucle sur la liste de ce type et de ses types parents, dans l'ordre du plus spécifique au plus
    # général
    type_parts = depense.type.split("-")
    type_mro = ["-".join(type_parts[:i]) for i in range(len(type_parts), 0, -1)]

    for type_depense in type_mro:
        if type_depense in compte.engagement_automatique:
            plafond = compte.engagement_automatique[type_depense]

            if depense.montant <= plafond:
                return True

            # Si un plafond est défini pour un type plus précis, soit il est plus élevé, et ça ne sert alors à rien
            # de tester le plafond moins contraignant vu qu'on ne respecte déjà pas celui-ci.
            # Soit il est moins élevé et vise à restreindre davantage ce sous-type de dépense, et on ne VEUT PAS
            # utiliser le plafond plus élevé défini pour le type plus général.
            break

    return False


def etat_initial(depense: Depense, createur: Role):
    compte = depense.compte

    # on vérifie si on a la permission sans référence au compte, parce que le ModelBackend qui gère par défaut
    # les permissions répond False dès que obj n'est pas None
    if createur.has_perm("gestion.engager_depense") or createur.has_perm(
        "gestion.engager_depense", obj=compte
    ):
        engager_depense(depense)
        return Depense.Etat.CONSTITUTION

    if createur.has_perm("gestion.gerer_depense") or createur.has_perm(
        "gestion.gerer_depense", obj=compte
    ):
        # il peut y a voir un plafond configuré pour ce type de dépense au-dessous duquel la dépense est engagée
        # automatiquement à sa création.
        if verifier_plafond_engagement(depense):
            return Depense.Etat.CONSTITUTION

        return Depense.Etat.ATTENTE_ENGAGEMENT

    return Depense.Etat.ATTENTE_VALIDATION


def todos(depense: Depense):
    todos = []
    todos_generaux = []

    if depense.etat == depense.Etat.ATTENTE_ENGAGEMENT:
        if not depense.documents.filter(Q(type=TypeDocument.DEVIS)).exists():
            todos_generaux.append(
                (
                    "Vous devez joindre le devis pour permettre l'engagement de la dépense par le responsable"
                    " du compte.",
                    NiveauTodo.IMPERATIF,
                )
            )
    else:
        if depense.etat == Depense.Etat.COMPLET and not depense.depense_reglee:
            todos_generaux.append(
                ("La dépense doit être réglée avant clôture.", NiveauTodo.IMPERATIF)
            )

        if not depense.documents.filter(type=TypeDocument.FACTURE).exists():
            todos_generaux.append(
                (
                    "Une facture (ou ticket de caisse) doit impérativement être joint à la dépense.",
                    NiveauTodo.IMPERATIF,
                ),
            )

        if todos_generaux:
            todos.append(("Obligations générales", todos_generaux))

        type_todos = []
        for type in CONDITIONS:
            if depense.type.startswith(type):
                for cond in CONDITIONS[type]:
                    if not cond.check(depense):
                        type_todos.append((cond.message_erreur, cond.niveau_erreur))

        if type_todos:
            todos.append(("Obligations pour ce type de dépense", type_todos))

    return todos
