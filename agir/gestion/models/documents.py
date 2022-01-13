import dynamic_filenames
import reversion
from django.db import models, transaction

from agir.gestion.models.common import ModeleGestionMixin, NumeroManager
from agir.gestion.typologies import TypeDocument
from agir.lib.models import TimeStampedModel


__all__ = ["Document", "VersionDocument"]


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


@reversion.register()
class Document(ModeleGestionMixin, TimeStampedModel):
    """Modèle représentant un élément justificatif, à associer à une instance d'un autre modèle de gestion"""

    objects = DocumentManager()

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

    search_config = (
        ("numero", "B"),
        ("titre", "A"),
        ("identifiant", "B"),
        ("description", "C"),
    )

    @property
    def fichier(self):
        return getattr(self.versions.last(), "fichier", None)

    class Meta:
        verbose_name = "Document justificatif"
        verbose_name_plural = "Documents justificatifs"


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
