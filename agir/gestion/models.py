import re
import secrets
from functools import reduce
from operator import add
from string import ascii_uppercase, digits

import dynamic_filenames
import reversion
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from agir.gestion.typologies import (
    TypeProjet,
    TypeDocument,
    TypeDepense,
    RoleParticipation,
    NiveauAcces,
)
from agir.lib.model_fields import IBANField
from agir.lib.models import LocationMixin, TimeStampedModel
from agir.lib.search import PrefixSearchQuery

ALPHABET = ascii_uppercase + digits

NUMERO_RE = re.compile("^[A-Z0-9]{3}-[A-Z0-9]{1,3}$")


def numero_unique():
    chars = [secrets.choice(ALPHABET) for _ in range(6)]
    return f"{''.join(chars[:3])}-{''.join(chars[3:])}"


class NumeroQueryset(models.QuerySet):
    def search(self, query):

        if NUMERO_RE.match(query):
            return self.filter(numero__startswith=query)

        search_config = self.model.search_config
        vector = reduce(
            add,
            (
                SearchVector(models.F(field), config=config, weight=weight)
                for field, config, weight in search_config
            ),
        )

        query = PrefixSearchQuery(
            query, config="french_unaccented"
        ) | PrefixSearchQuery(query, config="simple_unaccented")

        return (
            self.annotate(search=vector)
            .filter(search=query)
            .annotate(rank=SearchRank(vector, query))
            .order_by("-rank")
        )


class Commentaire(TimeStampedModel):
    class Type(models.TextChoices):
        REM = "R", "Remarque"
        WARN = "W", "Point de vigilance"
        TODO = "T", "À faire"

    auteur = models.ForeignKey(
        to="people.Person",
        verbose_name="Auteur⋅ice",
        on_delete=models.SET_NULL,
        related_name="+",
        null=True,
    )

    auteur_nom = models.CharField(
        verbose_name="Nom de l'auteur",
        blank=False,
        max_length=200,
        help_text="Pour pouvoir afficher un nom si la personne a été supprimée.",
    )

    type = models.CharField(
        verbose_name="Type de commentaire", max_length=1, choices=Type.choices
    )

    texte = models.TextField(verbose_name="Texte du commentaire", blank=False)

    cache = models.BooleanField(verbose_name="Commentaire caché", default=False)

    def get_auteur_display(self):
        if self.auteur:
            disp = str(self.auteur)
            if self.auteur_nom != disp:
                self.auteur_nom = disp
                self.save(update_fields=["auteur_nom"])
            return str(disp)
        else:
            return self.auteur_nom

    class Meta:
        ordering = ("created",)


class NumeroManager(models.Manager):
    def get_queryset(self):
        return NumeroQueryset(self.model, using=self._db)

    def get_by_natural_key(self, numero):
        return self.get(numero=numero)


class NumeroUniqueMixin(models.Model):
    objects = NumeroManager()

    numero = models.CharField(
        verbose_name="Numéro unique",
        max_length=7,
        editable=False,
        blank=False,
        default=numero_unique,
        unique=True,
        help_text="Numéro unique pour identifier chaque objet sur la plateforme.",
    )

    commentaires = models.ManyToManyField(
        to="Commentaire",
        verbose_name="Commentaires",
        help_text="Ces commentaires permettent d'ajouter de garder la trace des opérations de traitement des différentes pièces.",
    )

    def __str__(self):
        titre = f"{self.titre[70:]}..." if len(self.titre) > 70 else self.titre
        return f"« {titre} » ({self.numero})"

    class Meta:
        abstract = True


@reversion.register()
class Document(NumeroUniqueMixin, TimeStampedModel):
    class Besoin(models.TextChoices):
        NECESSAIRE = "NEC", "Strictement nécessaire"
        PREFERABLE = "PRE", "Préférable"
        IGNORER = "IGN", "Peut être ignoré"

    titre = models.CharField(
        verbose_name="Titre du document",
        help_text="Titre permettant d'identifier le document",
        max_length=200,
    )

    identifiant = models.CharField(
        verbose_name="Identifiant ou numéro externe",
        max_length=100,
        blank=True,
        help_text="Indiquez ici si ce document a un identifiant ou un numéro (numéro de facture ou de devis, identifiant de transaction, etc.)",
    )

    type = models.CharField(
        verbose_name="Type de document", max_length=10, choices=TypeDocument.choices
    )

    requis = models.CharField(
        verbose_name="Obligatoire ?", max_length=3, choices=Besoin.choices
    )

    description = models.TextField(
        "Description du document",
        help_text="Toute description complémentaire nécessaire pour identifier clairement le document (et le rechercher)",
        blank=True,
    )

    fichier = models.FileField(
        verbose_name="Fichier du document",
        null=True,
        blank=True,
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="gestion/documents/{uuid:.2base32}/{uuid}{ext}"
        ),
    )

    search_config = (
        ("numero", "simple_unaccented", "B"),
        ("titre", "french_unaccented", "A"),
        ("identifiant", "simple_unaccented", "B"),
        ("description", "french_unaccented", "C"),
    )

    class Meta:
        verbose_name = "Document justificatif"
        verbose_name_plural = "Documents justificatifs"


@reversion.register()
class Compte(TimeStampedModel):
    """Le compte regroupe un ensemble de dépenses

    Il est identifié par son nom et par une désignation courte (max 5 caractères)
    qui permet de le saisir rapidement dans les formulaires.
    """

    designation = models.CharField(
        verbose_name="Désignation courte", max_length=5, blank=False, unique=True
    )
    nom = models.CharField(
        verbose_name="Nom complet du compte", max_length=200, blank=False
    )
    description = models.TextField(verbose_name="Description", blank=True)

    def __str__(self):
        return f"{self.nom} ({self.designation})"

    class Meta:
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"
        permissions = [
            (
                "acces_contenu_restreint",
                "Voir les projets, dépenses et documents dont l'accès est indiqué comme restreint.",
            ),
            (
                "acces_contenu_secret",
                "Voir les projets, dépenses et documents dont l'accès est indiqué commme secret.",
            ),
        ]


@reversion.register(follow=["documents", "depenses"])
class Projet(NumeroUniqueMixin, TimeStampedModel):
    """Le projet regroupe ensemble des dépenses liées entre elles

    Un projet peut correspondre à un événement, ou à un type de de dépense précis.
    (par exemple « organisation du meeting du 16 janvier » ou « paiement salaire mars »)
    """

    class StatutProjet(models.TextChoices):
        DEMANDE_FINANCEMENT = "DFI", "Demande de financement"
        EN_CONSTITUTION = "ECO", "En cours de constitution"
        FINALISE = "FIN", "Finalisé par le secrétariat"
        RENVOI = "REN", "Renvoyé par l'équipe financière"

    titre = models.CharField(verbose_name="Titre du projet", max_length=40)
    type = models.CharField(
        verbose_name="Type de projet", choices=TypeProjet.choices, max_length=10
    )
    statut = models.CharField(
        verbose_name="Statut", max_length=3, choices=StatutProjet.choices, blank=False
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

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"


@reversion.register(follow=["documents"])
class Depense(NumeroUniqueMixin, TimeStampedModel):
    """Une dépense correspond à un paiement réalisé en lien avec une facture
    """

    class Etat(models.TextChoices):
        ATTENTE_ENGAGEMENT = "A", "En attente de l'engagement de la dépense"
        CONSTITUTION = "C", "Constitution du dossier"
        COMPLET = "O", "Dossier complété"
        CLOTURE = "L", "Dossier clôturé"

    class Validation(models.IntegerChoices):
        NON_VALIDE = 0, "Pas encore de validation"
        ORGANISATEUR = 1, "Validation organisateur"
        FINANCIERE = 2, "Validation financière"

    validation_etat = {
        Validation.NON_VALIDE: Etat.CONSTITUTION,
        Validation.ORGANISATEUR: Etat.COMPLET,
        Validation.FINANCIERE: Etat.CLOTURE,
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
        related_name="depenses",
        related_query_name="depense",
        help_text="Le projet éventuel auquel est rattaché cette dépense.",
        on_delete=models.SET_NULL,
    )

    type = models.CharField(
        "Type de dépense", max_length=5, choices=TypeDepense.hierarchical_choices()
    )

    montant = models.DecimalField(
        verbose_name="Montant de la dépense",
        decimal_places=2,
        null=False,
        max_digits=10,
    )

    validation = models.IntegerField(
        verbose_name="Validation du dossier de la dépense",
        choices=Validation.choices,
        default=Validation.NON_VALIDE,
        null=False,
    )

    date_depense = models.DateField(
        "Date d'engagement de la dépense",
        blank=True,
        null=True,
        help_text="Date à laquelle la dépense a été engagée (généralement l'acceptation du contrat)",
    )

    documents = models.ManyToManyField(
        to="Document", related_name="depenses", related_query_name="depense",
    )

    fournisseur = models.ForeignKey(
        "Fournisseur", null=True, blank=True, on_delete=models.SET_NULL
    )

    personnes = models.ManyToManyField(
        to="people.Person",
        verbose_name="Personnes concernées",
        related_name="depenses",
        related_query_name="depense",
        blank=True,
    )

    niveau_acces = models.CharField(
        verbose_name="Niveau d'accès",
        max_length=1,
        choices=NiveauAcces.choices,
        blank=False,
        default=NiveauAcces.SANS_RESTRICTION,
    )

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
    def etat(self):
        if not self.date_depense:
            return self.Etat.ATTENTE_ENGAGEMENT

        # noinspection PyTypeChecker
        return self.validation_etat[self.validation]

    def todos(self):
        from .actions.depenses import todo

        return todo(self)

    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"


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
        to=Depense,
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
        verbose_name="Date du règlement", blank=False, null=False, default=timezone.now,
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
        to="Fournisseur", null=True, blank=True, on_delete=models.SET_NULL,
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
        "adresse (1ère ligne)", max_length=100, blank=True
    )
    location_city_fournisseur = models.CharField("ville", max_length=100, blank=False)
    location_zip_fournisseur = models.CharField(
        "code postal", max_length=20, blank=False
    )
    location_country_fournisseur = CountryField(
        "pays", blank_label="(sélectionner un pays)", default="FR", blank=False
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


class Participation(TimeStampedModel):
    """Ce modèle associe des personnes à des projets, et indique leur rôle sur le projet
    """

    projet = models.ForeignKey(
        to=Projet,
        verbose_name="Projet",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    person = models.ForeignKey(
        to="people.Person",
        verbose_name="Personne",
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
    role = models.CharField(
        verbose_name="Rôle sur ce projet",
        max_length=3,
        choices=RoleParticipation.choices,
    )

    precisions = models.TextField(verbose_name="Précisions", blank=True)

    class Meta:
        verbose_name = "participation à un projet"
        verbose_name_plural = "participations à des projets"
        unique_together = ("projet", "person", "role")
