import uuid

import reversion
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from dynamic_filenames import FilePattern

from agir.donations.model_fields import BalanceField
from agir.lib.data import departements_choices
from agir.lib.display import display_price
from agir.lib.history import HistoryMixin
from agir.lib.model_fields import IBANField
from agir.lib.models import TimeStampedModel
from agir.payments.model_fields import AmountField

__all__ = [
    "AllocationModelMixin",
    "Operation",
    "DepartementOperation",
    "CNSOperation",
    "Spending",
    "SpendingRequest",
    "Document",
    "MonthlyAllocation",
]


class AllocationModelMixin(models.Model):
    TYPE_GROUP = "group"
    TYPE_DEPARTEMENT = "departement"
    TYPE_CNS = "cns"
    TYPE_CHOICES = (
        (TYPE_GROUP, _("à un groupe d'action")),
        (TYPE_DEPARTEMENT, _("à une caisse départementale")),
        (TYPE_CNS, _("à la caisse nationale de solidarité")),
    )

    type = models.CharField(
        "type",
        null=False,
        blank=False,
        choices=TYPE_CHOICES,
        default=TYPE_GROUP,
        max_length=200,
    )

    amount = models.SmallIntegerField("montant", null=False, blank=False)

    group = models.ForeignKey(
        to="groups.SupportGroup",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="subscriptions",
    )

    departement = models.CharField(
        "département",
        null=True,
        blank=True,
        choices=departements_choices,
        default=None,
        max_length=200,
    )

    def __str__(self):
        return "Allocation n°" + str(self.pk)

    def to_dict(self):
        return {
            "pk": self.pk,
            "type": self.type,
            "amount": self.amount,
            "group": self.group,
            "departement": self.departement,
        }

    class Meta:
        abstract = True


class OperationModelMixin(TimeStampedModel):
    amount = BalanceField(
        _("montant net"),
        null=False,
        blank=False,
        help_text=_(
            "La valeur doit être positive pour une augmentation d'allocation et négative pour une diminution."
        ),
    )
    payment = models.ForeignKey(
        to="payments.Payment",
        null=True,
        editable=False,
        blank=True,
        on_delete=models.PROTECT,
    )
    comment = models.TextField("Commentaire", blank=True, null=False)

    def validate_balance(self, errors):
        return errors

    def validate_unique(self, exclude=None):
        try:
            super().validate_unique(exclude)
        except ValidationError as e:
            errors = e.message_dict
        else:
            errors = {}

        errors = self.validate_balance(errors)

        if errors:
            raise ValidationError(errors)

    class Meta:
        abstract = True


class Operation(OperationModelMixin):
    group = models.ForeignKey(
        verbose_name="Groupe d'action",
        to="groups.SupportGroup",
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        related_name="operations",
        related_query_name="operation",
    )

    def validate_balance(self, errors=dict):
        from agir.donations.allocations import get_supportgroup_balance

        if self.group and isinstance(self.amount, int) and self.amount < 0:
            balance = get_supportgroup_balance(self.group)

            if balance + self.amount < 0:
                errors.setdefault("amount", []).append(
                    ValidationError(
                        f"La balance d'un groupe ne peut pas devenir négative (actuellement : {display_price(balance)})",
                        code="negative_balance",
                    )
                )

        return errors

    class Meta:
        verbose_name = "Opération"
        verbose_name_plural = "Opérations"
        unique_together = ("payment", "group")


class DepartementOperation(OperationModelMixin):
    departement = models.CharField(
        "Département",
        null=False,
        blank=False,
        choices=departements_choices,
        max_length=200,
    )

    def validate_balance(self, errors=dict):
        from agir.donations.allocations import get_departement_balance

        if self.departement and isinstance(self.amount, int) and self.amount < 0:
            balance = get_departement_balance(self.departement)

            if balance + self.amount < 0:
                errors.setdefault("amount", []).append(
                    ValidationError(
                        f"La balance d'un département ne peut pas devenir négative (actuellement : {display_price(balance)})",
                        code="negative_balance",
                    )
                )

        return errors

    class Meta:
        verbose_name = "Opération départementale"
        verbose_name_plural = "Opérations départementales"
        unique_together = ("payment", "departement")


class CNSOperation(OperationModelMixin):
    def validate_balance(self, errors=dict):
        from agir.donations.allocations import get_cns_balance

        if isinstance(self.amount, int) and self.amount < 0:
            balance = get_cns_balance()

            if balance + self.amount < 0:
                errors.setdefault("amount", []).append(
                    ValidationError(
                        f"La balance de la caisse nationale de solidarité ne peut pas devenir négative (actuellement : {display_price(balance)})",
                        code="negative_balance",
                    )
                )

        return errors

    class Meta:
        verbose_name = "Opération CNS"
        verbose_name_plural = "Opérations CNS"
        unique_together = ("payment",)


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
class SpendingRequest(HistoryMixin, TimeStampedModel):
    DIFFED_FIELDS = [
        "title",
        "event",
        "category",
        "category_precisions",
        "explanation",
        "amount",
        "spending_date",
        "provider",
        "iban",
    ]

    STATUS_DRAFT = "D"
    STATUS_AWAITING_GROUP_VALIDATION = "G"
    STATUS_AWAITING_REVIEW = "R"
    STATUS_AWAITING_SUPPLEMENTARY_INFORMATION = "I"
    STATUS_VALIDATED = "V"
    STATUS_TO_PAY = "T"
    STATUS_PAID = "P"
    STATUS_REFUSED = "B"
    STATUS_CHOICES = (
        (STATUS_DRAFT, _("Brouillon à compléter")),
        (
            STATUS_AWAITING_GROUP_VALIDATION,
            _("En attente de validation par un autre animateur"),
        ),
        (
            STATUS_AWAITING_REVIEW,
            _(
                "En attente de vérification par l'équipe de suivi des questions financières"
            ),
        ),
        (
            STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
            _("Informations supplémentaires requises"),
        ),
        (STATUS_VALIDATED, _("Validée, en attente des fonds")),
        (STATUS_TO_PAY, _("Décomptée de l'allocation du groupe, à payer")),
        (STATUS_PAID, _("Payée")),
        (STATUS_REFUSED, _("Cette demande a été refusée")),
    )

    STATUS_NEED_ACTION = {
        STATUS_DRAFT,
        STATUS_AWAITING_GROUP_VALIDATION,
        STATUS_AWAITING_SUPPLEMENTARY_INFORMATION,
        STATUS_VALIDATED,
    }
    STATUS_ADMINISTRATOR_ACTION = {STATUS_AWAITING_REVIEW, STATUS_TO_PAY}
    STATUS_EDITION_MESSAGES = {
        STATUS_AWAITING_REVIEW: "Votre requête a déjà été transmise ! Si vous l'éditez, il vous faudra la retransmettre à nouveau.",
        STATUS_VALIDATED: "Votre requête a déjà été validée par l'équipe de suivi des questions financières. Si vous l'éditez, il vous faudra recommencer le processus de validation.",
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

    HISTORY_MESSAGES = {
        STATUS_DRAFT: "Création de la demande",
        STATUS_AWAITING_GROUP_VALIDATION: "Validé par l'auteur d'origine",
        STATUS_AWAITING_REVIEW: "Renvoyé pour validation à l'équipe de suivi des questions financières",
        STATUS_AWAITING_SUPPLEMENTARY_INFORMATION: "Informations supplémentaires requises",
        STATUS_VALIDATED: "Demande validée par l'équipe de suivi des questions financières",
        STATUS_TO_PAY: "Demande en attente de réglement",
        STATUS_PAID: "Demande réglée",
        STATUS_REFUSED: "Demande rejetée par l'équipe de suivi des questions financières",
        (
            STATUS_AWAITING_GROUP_VALIDATION,
            STATUS_AWAITING_REVIEW,
        ): "Validé par un⋅e second⋅e animateur⋅rice",
    }
    for status, label in STATUS_CHOICES:
        HISTORY_MESSAGES[(status, status)] = "Modification de la demande"

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

    iban = IBANField(
        _("RIB (format IBAN)"),
        blank=False,
        null=False,
        help_text=_(
            "Indiquez le RIB du prestataire s'il s'agit d'un réglement, ou le RIB de la personne qui a payé s'il s'agit"
            " d'un remboursement."
        ),
        allowed_countries=["FR"],
    )

    payer_name = models.CharField(
        _("Nom de la personne qui a payé"),
        blank=True,
        max_length=200,
        help_text="S'il s'agit du remboursement d'une dépense déjà faite, indiquez le nom de la personne qui a payé"
        " et à qui l'IBAN correspond. Sinon, laissez vide.",
    )

    class Meta:
        permissions = (
            ("review_spendingrequest", _("Peut traiter les demandes de dépenses")),
        )
        verbose_name = "Demande de dépense ou remboursement"
        verbose_name_plural = "Demandes de dépense ou remboursement"

    # noinspection PyMethodOverriding
    @classmethod
    def get_history_step(cls, old, new, *, admin=False, **kwargs):
        old_fields = old.field_dict if old else {}
        new_fields = new.field_dict
        old_status, new_status = old_fields.get("status"), new_fields["status"]
        revision = new.revision
        person = revision.user.person if revision and revision.user else None

        res = {
            "modified": new_fields["modified"],
            "comment": revision.get_comment(),
            "diff": cls.get_diff(old_fields, new_fields) if old_fields else [],
        }

        if person and admin:
            res["user"] = format_html(
                '<a href="{url}">{text}</a>',
                url=reverse("admin:people_person_change", args=[person.pk]),
                text=person.get_short_name(),
            )
        elif person:
            res["user"] = person.get_short_name()
        else:
            res["user"] = "Équipe de suivi"

        # cas spécifique : si on revient à "attente d'informations supplémentaires suite à une modification par un non admin
        # c'est forcément une modification
        if (
            new_status == cls.STATUS_AWAITING_SUPPLEMENTARY_INFORMATION
            and person is not None
        ):
            res["title"] = "Modification de la demande"
        # some couples (old_status, new_status)
        elif (old_status, new_status) in cls.HISTORY_MESSAGES:
            res["title"] = cls.HISTORY_MESSAGES[(old_status, new_status)]
        else:
            res["title"] = cls.HISTORY_MESSAGES.get(
                new_status, "[Modification non identifiée]"
            )

        return res


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


class MonthlyAllocation(AllocationModelMixin):
    subscription = models.ForeignKey(
        "payments.Subscription", related_name="allocations", on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "Allocation mensuelle"
        verbose_name_plural = "Allocations mensuelles"
