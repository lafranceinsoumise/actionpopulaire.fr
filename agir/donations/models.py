import uuid

import reversion
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _
from dynamic_filenames import FilePattern
from reversion.models import Revision, Version

from agir.donations.model_fields import AmountField
from agir.lib.models import TimeStampedModel


class Operation(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    group = models.ForeignKey(
        to="groups.SupportGroup",
        null=False,
        editable=False,
        blank=False,
        on_delete=models.PROTECT,
    )
    amount = models.IntegerField(
        _("opération en centimes d'euros"), null=False, blank=False, editable=False
    )
    payment = models.OneToOneField(
        to="payments.Payment",
        null=True,
        editable=False,
        blank=True,
        on_delete=models.PROTECT,
    )


class Spending(Operation):
    """
    Utility class to use when playing with spending operations.
    """

    def save(self, *args, **kwargs):
        if self.amount > 0:
            raise Exception("Spendings must be negative")

        super().save(*args, **kwargs)

    class Meta:
        proxy = True


@reversion.register(follow=["documents"])
class SpendingRequest(TimeStampedModel):
    STATUS_DRAFT = "D"
    STATUS_AWAITING_GROUP_VALIDATION = "G"
    STATUS_AWAITING_REVIEW = "R"
    STATUS_AWAITING_SUPPLEMENTARY_INFORMATION = "I"
    STATUS_VALIDATED = "V"
    STATUS_TO_PAY = "T"
    STATUS_PAID = "P"
    STATUS_CHOICES = (
        (STATUS_DRAFT, _("Brouillon à compléter")),
        (
            STATUS_AWAITING_GROUP_VALIDATION,
            _("En attente de validation par un autre animateur"),
        ),
        (STATUS_AWAITING_REVIEW, _("En attente de vérification par la Trésorerie")),
        (
            STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
            _("Informations supplémentaires requises"),
        ),
        (STATUS_VALIDATED, _("Validée, en attente des fonds")),
        (STATUS_TO_PAY, _("Décomptée de l'allocation du groupe, à payer")),
        (STATUS_PAID, _("Payée")),
    )

    STATUS_NEED_ACTION = {
        STATUS_DRAFT,
        STATUS_AWAITING_GROUP_VALIDATION,
        STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
    }
    STATUS_ADMINISTRATOR_ACTION = {
        STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
        STATUS_VALIDATED,
        STATUS_PAID,
    }

    CATEGORY_HARDWARE = "H"
    CATEGORY_VENUE = "V"
    CATEGORY_SERVICE = "S"
    CATEGORY_OTHER = "O"
    CATEGORY_CHOICES = (
        (CATEGORY_HARDWARE, _("Matériel militant")),
        (CATEGORY_VENUE, _("Location d'une salle")),
        (CATEGORY_SERVICE, _("Prestation de service")),
        (CATEGORY_SERVICE, _("Autres")),
    )

    id = models.UUIDField(_("Identifiant"), primary_key=True, default=uuid.uuid4)

    title = models.CharField(_("Titre"), max_length=200)
    status = models.CharField(
        _("Statut"), max_length=1, default=STATUS_DRAFT, choices=STATUS_CHOICES
    )

    operation = models.ForeignKey(
        Operation, on_delete=models.PROTECT, related_name="spending_request", null=True
    )

    group = models.ForeignKey(
        "groups.SupportGroup",
        on_delete=models.PROTECT,
        related_name="spending_requests",
        related_query_name="spending_request",
        blank=False,
        null=False,
    )
    event = models.ForeignKey(
        "events.Event",
        verbose_name=_("Événement lié à la dépense"),
        on_delete=models.SET_NULL,
        related_name="spending_requests",
        related_query_name="spending_request",
        blank=True,
        null=True,
        help_text=_(
            "Si c'est pertinent, l'événement concerné par la dépense. Il doit être organisé par le groupe pour"
            " pouvoir être sélectionné."
        ),
    )

    category = models.CharField(
        _("Catégorie de demande"),
        max_length=1,
        blank=False,
        null=False,
        choices=CATEGORY_CHOICES,
    )
    category_precisions = models.CharField(
        _("Précisions sur le type de demande"), max_length=260, blank=False, null=False
    )

    explanation = models.TextField(
        _("Justification de la demande"),
        max_length=1500,
        help_text=_(
            "Merci de justifier votre demande. Longueur conseillée : 500 signes."
        ),
    )

    amount = AmountField(
        _("Montant de la dépense"),
        null=False,
        blank=False,
        help_text=_(
            "Pour que cette demande soit payée, la somme allouée à votre groupe doit être suffisante."
        ),
    )

    spending_date = models.DateField(
        _("Date de la dépense"),
        blank=False,
        null=False,
        help_text=_(
            "Si la dépense n'a pas encore été effectuée, merci d'indiquer la date probable à laquelle elle surviendra."
        ),
    )

    provider = models.CharField(
        _("Raison sociale du prestataire"), blank=False, null=False, max_length=200
    )

    iban = models.CharField(
        _("RIB (format IBAN)"),
        blank=False,
        null=False,
        max_length=100,
        help_text=_(
            "Indiquez le RIB du prestataire s'il s'agit d'un réglement, ou le RIB de la personne concernée s'il s'agit d'un remboursement."
        ),
    )


document_path = FilePattern(
    filename_pattern="financement/request/{instance.request_id}/{uuid:s}{ext}"
)


@reversion.register()
class Document(models.Model):
    TYPE_INVOICE = "I"
    TYPE_PICTURE = "P"
    TYPE_OTHER = "O"
    TYPE_CHOICES = (
        (TYPE_INVOICE, _("Facture")),
        (
            TYPE_PICTURE,
            _("Photo ou illustration de l'événement, de la salle, du matériel"),
        ),
        (TYPE_OTHER, _("Autre type de justificatif")),
    )

    title = models.CharField(
        _("Titre du document"), null=False, blank=False, max_length=200
    )
    request = models.ForeignKey(
        SpendingRequest,
        on_delete=models.CASCADE,
        related_name="documents",
        related_query_name="document",
        null=False,
        blank=False,
    )

    type = models.CharField(
        _("Type de document"), blank=False, max_length=1, choices=TYPE_CHOICES
    )

    file = models.FileField(
        _("Fichier"),
        upload_to=document_path,
        validators=[
            validators.FileExtensionValidator(
                [
                    "doc",
                    "docx",
                    "odt",
                    "xls",
                    "xlsx",
                    "ods",
                    "pdf",
                    "png",
                    "jpeg",
                    "jpg",
                    "gif",
                ]
            )
        ],
    )

    deleted = models.BooleanField(_("Supprimé"), null=False, default=False)
