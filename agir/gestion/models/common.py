from functools import reduce
from operator import add

import reversion
from agir.lib.model_fields import IBANField, BICField
from django.contrib.admin.options import get_content_type_for_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchRank, SearchVectorField
from django.db import models
from django.urls import reverse

from agir.gestion.models.configuration import EngagementAutomatique
from agir.lib.models import TimeStampedModel
from agir.lib.search import PrefixSearchQuery

__all__ = ("Compte", "InstanceCherchable", "Autorisation")

from agir.lib.utils import NUMERO_RE, numero_unique


class SearchableQueryset(models.QuerySet):
    def search(self, query):
        if NUMERO_RE.match(query):
            return self.filter(numero__startswith=query)

        vector = self.model.search_vector()

        query = PrefixSearchQuery(
            query, config="french_unaccented"
        ) | PrefixSearchQuery(query, config="simple_unaccented")

        return (
            self.annotate(search=vector)
            .filter(search=query)
            .annotate(rank=SearchRank(vector, query))
            .order_by("-rank")
        )


class NumeroManager(models.Manager.from_queryset(SearchableQueryset)):
    def get_by_natural_key(self, numero):
        return self.get(numero=numero)


class SearchableModel(models.Model):
    objects = SearchableQueryset.as_manager()

    @classmethod
    def search_vector(cls):
        search_config = cls.search_config
        return reduce(
            add,
            (
                SearchVector(
                    models.F(field),
                    config="french_unaccented",
                    weight=weight,
                )
                for field, weight in search_config
            ),
        )

    class Meta:
        abstract = True


class ModeleGestionMixin(SearchableModel):
    """Mixin à intégrer pour les modèles utilisés dans l'application de gestion

    Ce mixin ajoute trois fonctionnalités principales :
    - le système de numéro unique généré aléatoirement à la création qui permet de se référer à n'importe quelle
      instance de façon unique
    - le système de commentaires qui permet d'ajouter des remarques ou des todos sur mesure à chaque élément
      de gestion.
    - un système de configuration de recherche plein texte.

    Une méthode `__str__` par défaut est aussi fournie si le modèle a un champ `titre`.
    """

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
        titre = f"{self.titre[:70]}..." if len(self.titre) > 70 else self.titre
        return f"« {titre} » ({self.numero})"

    class Meta:
        abstract = True


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

    actif = models.BooleanField(verbose_name="Compte actif", default=True)

    emetteur_designation = models.CharField(
        verbose_name="Désignation bancaire d'émetteur",
        max_length=140,
        blank=True,
        help_text="La désignation bancaire utilisée pour émettre des virements à partir de ce compte.",
    )

    emetteur_iban = IBANField(
        verbose_name="IBAN émetteur",
        help_text="L'IBAN utilisé pour émettre des virements à partir de ce compte.",
        blank=True,
    )

    emetteur_bic = BICField(
        verbose_name="BIC émetteur",
        help_text="Le BIC utilisé pour émettre des virements à partir de ce compte.",
        blank=True,
    )

    beneficiaire_designation = models.CharField(
        verbose_name="Désignation bancaire de créditeur",
        max_length=140,
        blank=True,
        help_text="La désignation bancaire utilisée comme créditeur pour un virement vers ce compte (pour une "
        "refacturation par exemple).",
    )

    beneficiaire_iban = IBANField(
        verbose_name="IBAN émetteur",
        help_text="L'IBAN utilisé comme créditeur pour un virement vers ce compte.",
        blank=True,
    )

    beneficiaire_bic = BICField(
        verbose_name="BIC émetteur",
        help_text="Le BIC utilisé comme créditeur pour un virement vers ce compte.",
        blank=True,
    )

    configuration = models.JSONField(
        verbose_name="Configuration",
        default=dict,
        null=False,
        blank=True,
    )

    engagement_automatique = EngagementAutomatique()

    def __str__(self):
        return f"{self.designation}"

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
            ("gerer_depense", "Gérer les dépenses après engagement"),
            ("controler_depense", "Contrôler les dépenses a posteriori"),
            ("validation_depense", "Validation comptable des dépenses"),
            ("voir_montant_depense", "Voir le montant des dépenses finalisées"),
            ("gerer_projet", "Gérer les projets"),
            ("controler_projet", "Contrôler les projets"),
        ]


class Autorisation(TimeStampedModel):
    """Une autorisation permet d'attribuer à un groupe des permissions sur un compte en particulier"""

    compte = models.ForeignKey(
        to="Compte",
        on_delete=models.CASCADE,
        related_name="autorisations",
        related_query_name="autorisation",
    )

    group = models.ForeignKey(
        to="auth.Group",
        on_delete=models.CASCADE,
        related_name="+",
    )

    autorisations = ArrayField(models.CharField(max_length=100), default=list)


class InstanceCherchable(models.Model):
    numero = models.CharField(
        verbose_name="Numéro unique",
        max_length=7,
        editable=False,
        blank=True,
        default=numero_unique,
        unique=True,
        help_text="Numéro unique pour identifier chaque objet sur la plateforme.",
    )
    recherche = SearchVectorField(verbose_name="Champ de recherche", null=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    instance = GenericForeignKey()

    @classmethod
    def mettre_a_jour(cls, instance):
        model = instance._meta.model
        content_type = get_content_type_for_model(instance)
        instance_qs = model.objects.filter(pk=instance.pk)

        InstanceCherchable.objects.update_or_create(
            numero=instance_qs.values("numero"),
            content_type=content_type,
            object_id=instance.pk,
            defaults={"recherche": instance_qs.values(v=model.search_vector())},
        )

    def lien_admin(self):
        return reverse(
            f"admin:gestion_{self.content_type.model}_change", args=(self.object_id,)
        )

    class Meta:
        verbose_name = "Recherche"
        verbose_name_plural = "Recherche"
        indexes = (GinIndex(fields=("recherche",)),)
