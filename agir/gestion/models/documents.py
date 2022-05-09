import re

import dynamic_filenames
import reversion
from django.core.validators import RegexValidator
from django.db import models, transaction

from agir.gestion.models.common import ModeleGestionMixin, NumeroManager
from agir.gestion.typologies import TypeDocument
from agir.lib.models import TimeStampedModel


__all__ = ["Document", "VersionDocument"]


NUMERO_PIECE_REF_RE = re.compile(
    r"^(?P<compte>\d{5})(?P<departement>\d\d[\dAB])(?P<ordre>\d{4})$"
)


class DocumentManager(NumeroManager):
    def create(self, fichier=None, **kwargs):
        with transaction.atomic():
            document = super().create(**kwargs)

            if fichier is not None:
                VersionDocument.objects.create(
                    document=document,
                    titre="Version initiale",
                    fichier=fichier,
                )

        return document


@reversion.register(follow=("versions",))
class Document(ModeleGestionMixin, TimeStampedModel):
    """Modèle représentant un élément justificatif, à associer à une instance d'un autre modèle de gestion"""

    objects = DocumentManager()

    class Besoin(models.TextChoices):
        NECESSAIRE = "NEC", "Strictement nécessaire"
        PREFERABLE = "PRE", "Préférable"
        IGNORER = "IGN", "Peut être ignoré"

    precision = models.CharField(
        verbose_name="Précision sur la nature du document",
        help_text="Titre permettant d'identifier le document",
        max_length=200,
        blank=True,
    )

    identifiant = models.CharField(
        verbose_name="Numéro ou identifiant",
        max_length=100,
        blank=True,
        help_text="Indiquez ici si ce document a un identifiant ou un numéro (numéro de facture ou de devis, identifiant de transaction, etc.)",
    )

    numero_piece = models.CharField(
        verbose_name="Numéro de pièce justificative",
        max_length=12,
        validators=(RegexValidator(regex=NUMERO_PIECE_REF_RE),),
        unique=True,
        blank=True,
        null=True,
        help_text="Le numéro de pièce justificative à utiliser pour l'export vers FinPol.",
    )

    date = models.DateField(
        verbose_name="Date du document",
        null=True,
        blank=True,
        help_text="Si le document a une date, indiquez-la ici.",
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

    search_config = (
        ("numero", "B"),
        ("precision", "A"),
        ("identifiant", "B"),
        ("description", "C"),
    )

    def __str__(self):
        s = self.get_type_display()
        if self.precision:
            s = f"{s} - {self.precision}"
        if not self.fichier:
            s = f"{s} (MANQUANT)"
        return s

    @property
    def fichier(self):
        return getattr(self.versions.last(), "fichier", None)

    class Meta:
        verbose_name = "Document justificatif"
        verbose_name_plural = "Documents justificatifs"


@reversion.register()
class VersionDocument(models.Model):
    document = models.ForeignKey(
        Document,
        blank=False,
        on_delete=models.CASCADE,
        related_name="versions",
        related_query_name="version",
    )

    date = models.DateTimeField(
        "Date de téléchargement", auto_now_add=True, editable=False
    )

    titre = models.CharField(
        verbose_name="Titre de la version", max_length=200, blank=False
    )

    fichier = models.FileField(
        verbose_name="Fichier pour cette version",
        null=False,
        blank=False,
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="gestion/documents/{uuid:.2base32}/{uuid}{ext}"
        ),
    )

    class Meta:
        verbose_name = "Version"
        ordering = ("document", "date")
