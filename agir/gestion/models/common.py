import re
import secrets
from functools import reduce
from operator import add
from string import ascii_uppercase, digits

import dynamic_filenames
import reversion
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models

from agir.gestion.typologies import TypeDocument
from agir.lib.models import TimeStampedModel
from agir.lib.search import PrefixSearchQuery


__all__ = (
    "Document",
    "Compte",
)


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
        verbose_name="Obligatoire ?",
        max_length=3,
        choices=Besoin.choices,
        default=Besoin.NECESSAIRE,
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

    configuration = models.JSONField(
        verbose_name="Configuration", default=dict, null=False, blank=True
    )

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
            ("engager_depense", "Engager une dépense pour ce compte"),
            ("gerer_depense", "Gérer les dépenses"),
            ("controler_depense", "Contrôler les dépenses"),
            ("gerer_projet", "Gérer les projets"),
            ("controler_projet", "Contrôler les projets"),
        ]


class Autorisation(TimeStampedModel):
    """Une autorisation reliée à un compte en particulier.
    """

    compte = models.ForeignKey(
        to="Compte",
        on_delete=models.CASCADE,
        related_name="autorisations",
        related_query_name="autorisation",
    )

    group = models.ForeignKey(
        to="auth.Group", on_delete=models.CASCADE, related_name="+",
    )

    autorisations = ArrayField(models.CharField(max_length=100), default=list)
