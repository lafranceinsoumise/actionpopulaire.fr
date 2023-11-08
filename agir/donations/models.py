import uuid

import reversion
from django.contrib import admin
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Prefetch
from django.db.models.enums import ChoicesMeta
from django.template.defaultfilters import floatformat
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, ngettext
from dynamic_filenames import FilePattern
from reversion.models import Version

from agir.donations.model_fields import BalanceField, PositiveBalanceField
from agir.lib.admin.utils import admin_url
from agir.lib.data import departements_choices
from agir.lib.display import display_price
from agir.lib.history import HistoryMixin
from agir.lib.model_fields import IBANField, BICField
from agir.lib.models import TimeStampedModel
from agir.lib.utils import front_url
from agir.payments.model_fields import AmountField

__all__ = [
    "AllocationModelMixin",
    "AccountOperation",
    "SpendingRequest",
    "Document",
    "MonthlyAllocation",
]

spending_request_rib_path = FilePattern(
    filename_pattern="{app_label}/{model_name}/{instance.id}/{uuid:.8base32}{ext}"
)
spending_request_document_path = FilePattern(
    filename_pattern="{app_label}/{model_name}/{instance.request_id}/{uuid:.8base32}{ext}"
)


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

    @admin.display(description="Montant")
    def get_amount_display(self):
        if not isinstance(self.amount, int):
            return "-"

        return "{} €".format(floatformat(self.amount / 100, 2))

    class Meta:
        abstract = True


class AccountOperation(TimeStampedModel):
    datetime = models.DateTimeField(
        _("Date de l'opération"),
        default=timezone.now,
        null=False,
    )
    amount = PositiveBalanceField(
        _("montant"),
        null=False,
        blank=False,
    )

    source = models.CharField(
        _("Source"),
        null=False,
        blank=False,
        help_text=_("Le compte crédité, celui d'où vient la ressource"),
        max_length=200,
    )

    destination = models.CharField(
        _("Destination"),
        null=False,
        blank=False,
        help_text=_("Le compte débité, celui où va la ressource"),
        max_length=200,
    )

    payment = models.ForeignKey(
        to="payments.Payment",
        null=True,
        editable=False,
        blank=True,
        on_delete=models.PROTECT,
        related_name="account_operations",
        related_query_name="account_operation",
    )

    comment = models.TextField("Commentaire", blank=True, null=False)

    @admin.display(description="Montant")
    def get_amount_display(self):
        if not isinstance(self.amount, int):
            return "-"

        return "{} €".format(floatformat(self.amount / 100, 2))

    def __repr__(self):
        return f"AccountOperation(amount={self.amount!r}, source={self.source!r}, destination={self.destination!r})"

    def __str__(self):
        return f"Opération "

    class Meta:
        # pas besoin d'ajouter la source au deuxième index : si on veut chercher par source ET destination le premier
        # index suffit.
        indexes = [
            models.Index(
                fields=("source", "destination", "amount"),
                name="donations_accountop_source",
            ),
            models.Index(
                fields=("destination", "amount"),
                name="donations_accountop_dest",
            ),
        ]


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

    @admin.display(description="Montant")
    def get_amount_display(self):
        if not isinstance(self.amount, int):
            return "-"

        return "{} €".format(floatformat(self.amount / 100, 2))

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


class SpendingRequestQuerySet(models.QuerySet):
    def with_serializer_prefetch(self):
        return self.select_related("creator", "group", "event").prefetch_related(
            Prefetch(
                "documents",
                queryset=Document.objects.filter(deleted=False),
                to_attr="_pf_attachments",
            )
        )


@reversion.register(follow=["documents"])
class SpendingRequest(HistoryMixin, TimeStampedModel):
    objects = SpendingRequestQuerySet.as_manager()

    class Timing(models.TextChoices):
        PAST = "P", "Passée"
        UPCOMING = "U", "Future"

    class Status(models.TextChoices):
        DRAFT = "D", "Brouillon à compléter"
        AWAITING_PEER_REVIEW = (
            "G",
            "En attente de vérification par une autre personne",
        )
        AWAITING_ADMIN_REVIEW = (
            "R",
            "En attente de vérification par l'équipe de suivi des questions financières",
        )
        AWAITING_SUPPLEMENTARY_INFORMATION = (
            "I",
            "Informations supplémentaires requises",
        )
        VALIDATED = (
            "V",
            "Validée par l'équipe de suivi des questions financières, en attente des fonds",
        )
        TO_PAY = "T", "Décomptée de l'allocation du groupe, à payer"
        PAID = "P", "Payée"
        REFUSED = "B", "Cette demande a été refusée"

        @property
        def choice(self):
            return self.value, self.label

    class CategoryMeta(ChoicesMeta):
        @property
        def visible_choices(cls):
            return tuple(
                (value, label)
                for value, label in cls.choices
                if not value or len(value) == 2
            )

    class Category(models.TextChoices, metaclass=CategoryMeta):
        # Legacy categories
        HARDWARE = "H", "[Obsolète] Matériel militant"
        SERVICE = "S", "[Obsolète] Prestation de service"
        VENUE = "V", "[Obsolète] Location de salle"
        OTHER = "O", "[Obsolète] Autres"
        # Current categories
        IMPRESSIONS = "IM", "Impressions"
        CONSOMMABLES = "CO", "Achat de consommables (colles, feutres, … )"
        ACHAT = "AC", "Achat de matériel (quincaillerie, matériel de collage, … )"
        DEPLACEMENT = "DE", "Déplacement"
        HEBERGEMENT = "HE", "Hébergement"
        SALLE = "SA", "Location de salle"
        LOCATION = "MA", "Location de matériel (mobilier, vaisselle, … )"
        TECHNIQUE = "TE", "Location de matériel technique (sono, vidéo)"
        VEHICULE = "VE", "Location de véhicule"

    # List of fields that are required in order to send the request for review
    REQUIRED_FOR_REVIEW_FIELDS = [
        "title",
        "timing",
        "campaign",
        "amount",
        "status",
        "group",
        "category",
        "explanation",
        "spending_date",
        "contact_name",
        "contact_phone",
        "bank_account_name",
        "bank_account_iban",
        "bank_account_bic",
        "bank_account_rib",
        "attachments",
    ]

    DIFFED_FIELDS = [
        "title",
        "timing",
        "campaign",
        "amount",
        "category",
        "category_precision",
        "explanation",
        "event",
        "spending_date",
        "contact_name",
        "contact_email",
        "contact_phone",
        "bank_account_name",
        "bank_account_iban",
        "bank_account_bic",
        "bank_account_rib",
        "documents",
    ]

    HISTORY_MESSAGES = {
        Status.DRAFT: "Création de la demande",
        Status.AWAITING_PEER_REVIEW: "Validée par l'auteur d'origine",
        Status.AWAITING_ADMIN_REVIEW: "Renvoyée pour validation à l'équipe de suivi des questions financières",
        Status.AWAITING_SUPPLEMENTARY_INFORMATION: "Informations supplémentaires requises",
        Status.VALIDATED: "Demande validée par l'équipe de suivi des questions financières",
        Status.TO_PAY: "Demande en attente de règlement",
        Status.PAID: "Demande réglée",
        Status.REFUSED: "Demande rejetée par l'équipe de suivi des questions financières",
        (
            Status.AWAITING_PEER_REVIEW,
            Status.AWAITING_ADMIN_REVIEW,
        ): "Validée par un⋅e autre gestionnaire",
    }

    id = models.UUIDField(
        _("Identifiant"), primary_key=True, default=uuid.uuid4, editable=False
    )
    title = models.CharField(_("Titre"), max_length=200)
    timing = models.CharField(
        _("Type de dépense"),
        max_length=1,
        default="",
        choices=Timing.choices,
        blank=True,
        null=False,
    )
    campaign = models.BooleanField(
        "Dépense effectuée dans le cadre d'une campagne éléctorale",
        default=False,
        blank=False,
        null=False,
    )
    status = models.CharField(
        _("Statut"),
        max_length=1,
        default=Status.DRAFT,
        choices=Status.choices,
        blank=False,
        null=False,
    )

    account_operation = models.ForeignKey(
        AccountOperation,
        on_delete=models.PROTECT,
        related_name="spending_request",
        null=True,
    )

    operation = models.ForeignKey(
        Operation, on_delete=models.PROTECT, related_name="spending_request", null=True
    )
    creator = models.ForeignKey(
        "people.Person",
        verbose_name=_("Créateur·ice de la demande"),
        on_delete=models.SET_NULL,
        related_name="own_spending_requests",
        related_query_name="own_spending_request",
        blank=True,
        null=True,
        default=None,
    )
    group = models.ForeignKey(
        "groups.SupportGroup",
        verbose_name=_("Groupe lié la dépense"),
        on_delete=models.PROTECT,
        related_name="spending_requests",
        related_query_name="spending_request",
        blank=False,
        null=False,
    )
    category = models.CharField(
        _("Catégorie"),
        max_length=2,
        blank=False,
        null=False,
        choices=Category.choices,
    )
    category_precisions = models.CharField(
        _("Précisions sur le type de demande"), max_length=260, blank=True
    )
    explanation = models.TextField(
        _("Motif de l'achat"),
        max_length=1500,
        null=False,
        blank=True,
    )
    event = models.ForeignKey(
        "events.Event",
        verbose_name=_("Événement lié à la dépense"),
        on_delete=models.SET_NULL,
        related_name="spending_requests",
        related_query_name="spending_request",
        blank=True,
        null=True,
    )
    spending_date = models.DateField(
        _("Date de l'achat"),
        blank=True,
        null=False,
        help_text=_(
            "Si l'achat n'a pas encore été effectué, merci d'indiquer la date probable à laquelle celui-ci surviendra."
        ),
    )
    contact_name = models.CharField(
        _("Nom du contact"), max_length=255, blank=True, null=False, default=""
    )
    contact_email = models.EmailField(
        _("Adresse e-mail du contact"), blank=True, null=False, default=""
    )
    contact_phone = models.CharField(
        _("Numéro de téléphone du contact"),
        max_length=30,
        blank=True,
        null=False,
        default="",
    )
    amount = AmountField(
        _("Montant de la dépense"),
        null=False,
        blank=False,
    )
    payer_name = models.CharField(
        _("[Obsolète] Personne à payer"),
        max_length=200,
        null=True,
        blank=True,
    )
    bank_account_name = models.CharField(
        _("Titulaire du compte bancaire"), blank=True, null=False, max_length=200
    )
    bank_account_iban = IBANField(
        _("IBAN"), blank=True, null=False, allowed_countries=["FR"]
    )
    bank_account_bic = BICField(_("BIC"), blank=True, null=False)
    bank_account_rib = models.FileField(
        _("RIB"),
        upload_to=spending_request_rib_path,
        validators=[validators.FileExtensionValidator(["pdf", "png", "jpeg", "jpg"])],
        null=True,
        blank=True,
    )

    class Meta:
        permissions = (
            ("review_spendingrequest", _("Peut traiter les demandes de dépenses")),
        )
        verbose_name = "Demande de dépense ou remboursement"
        verbose_name_plural = "Demandes de dépense ou remboursement"

    @property
    def front_url(self):
        return front_url("spending_request_details", args=(self.pk,), absolute=True)

    @property
    def admin_url(self):
        return admin_url(
            "admin:donations_spendingrequest_change", args=(self.pk,), absolute=True
        )

    @property
    def admin_review_url(self):
        return admin_url(
            "admin:donations_spendingrequest_review", args=(self.pk,), absolute=True
        )

    @property
    def attachments(self):
        if hasattr(self, "_pf_attachments"):
            return list(self._pf_attachments)

        return list(self.documents.filter(deleted=False))

    @property
    def need_action(self):
        # Whether a user action is needed for the request
        return self.status in (
            self.Status.DRAFT,
            self.Status.AWAITING_PEER_REVIEW,
            self.Status.AWAITING_SUPPLEMENTARY_INFORMATION,
            self.Status.VALIDATED,
        )

    @property
    def need_admin_action(self):
        # Whether an admin action is needed for the request
        return self.status in (self.Status.AWAITING_ADMIN_REVIEW, self.Status.TO_PAY)

    @property
    def is_valid_amount(self):
        from agir.donations.allocations import get_supportgroup_balance

        return 0 < self.amount <= get_supportgroup_balance(self.group)

    @property
    def missing_fields(self):
        missing_fields = [
            field
            for field in self.REQUIRED_FOR_REVIEW_FIELDS
            if hasattr(self, field) and getattr(self, field) in [None, "", []]
        ]

        return missing_fields

    @property
    def editable(self):
        return self.status in (
            self.Status.DRAFT,
            self.Status.AWAITING_PEER_REVIEW,
            self.Status.AWAITING_SUPPLEMENTARY_INFORMATION,
        )

    @property
    def deletable(self):
        return self.status in (
            self.Status.DRAFT,
            self.Status.AWAITING_PEER_REVIEW,
        )

    @property
    def ready_for_review(self):
        return len(self.missing_fields) == 0 and self.is_valid_amount

    @property
    def done(self):
        return self.status in (self.Status.PAID, self.Status.REFUSED)

    @property
    def edition_warning(self):
        if self.status == self.Status.AWAITING_ADMIN_REVIEW:
            return (
                "Votre requête a déjà été transmise ! "
                "Si vous l'éditez, il vous faudra la retransmettre à nouveau."
            )

        if self.status == self.Status.VALIDATED:
            return (
                "Votre requête a déjà été validée par l'équipe de suivi des questions financières. "
                "Si vous l'éditez, il vous faudra recommencer le processus de validation."
            )

        return None

    @property
    def peer_reviewers(self):
        versions = (
            Version.objects.get_for_object(self)
            .order_by("pk")
            .select_related("revision__user")
        )
        return [
            version.revision.user
            for version in versions
            if version.field_dict["status"] == self.Status.AWAITING_PEER_REVIEW
        ]

    def can_peer_review(self, user):
        return self.peer_reviewers and user != self.peer_reviewers[0]

    def next_status(self, user):
        if self.status == self.Status.DRAFT and self.ready_for_review:
            return self.Status.AWAITING_PEER_REVIEW

        if (
            self.status == self.Status.AWAITING_PEER_REVIEW
            and self.ready_for_review
            and self.can_peer_review(user)
        ):
            return self.Status.AWAITING_ADMIN_REVIEW

        if (
            self.status == self.Status.AWAITING_SUPPLEMENTARY_INFORMATION
            and self.ready_for_review
        ):
            return self.Status.AWAITING_ADMIN_REVIEW

        if self.status == self.Status.VALIDATED and self.is_valid_amount:
            return self.Status.TO_PAY

        return None

    # noinspection PyMethodOverriding
    @classmethod
    def get_history_step(cls, old, new, **kwargs):
        from agir.donations.spending_requests import get_revision_comment

        step = super().get_history_step(old, new, **kwargs)

        old_fields = old.field_dict if old else {}
        new_fields = new.field_dict
        old_status, new_status = old_fields.get("status", None), new_fields["status"]

        step["title"] = get_revision_comment(old_status, new_status, step["person"])

        step["status"] = new_status

        if old_status and old_status != new_status:
            step["from_status"] = old_status

        if step["comment"] == step["title"]:
            step["comment"] = ""

        if step.get("diff", None) and not step["comment"]:
            step["comment"] = ngettext(
                f"Modification du champ : {step['diff'][0]}",
                f"Modification des champs : {', '.join(step['diff'])}",
                len(step["diff"]),
            )

        step["person"] = step["person"] or "Équipe de suivi"

        return step

    @classmethod
    def get_field_labels(cls, fields):
        from agir.donations.spending_requests import get_spending_request_field_labels

        return get_spending_request_field_labels(fields)


@reversion.register()
class Document(models.Model):
    class Type(models.TextChoices):
        ESTIMATE = "E", "Devis"
        INVOICE = "I", "Facture"
        PRINT_MASTER = "B", "Impression"
        PICTURE = "P", "Photo ou illustration de l'événement, de la salle, du matériel"
        OTHER = "O", "Autre type de justificatif"

    request = models.ForeignKey(
        SpendingRequest,
        verbose_name="Demande de dépense",
        on_delete=models.CASCADE,
        related_name="documents",
        related_query_name="document",
        null=False,
        blank=False,
    )
    title = models.CharField(
        _("Titre du document"), null=False, blank=False, max_length=200
    )
    type = models.CharField(
        _("Type de document"), blank=False, max_length=1, choices=Type.choices
    )
    file = models.FileField(
        _("Fichier"),
        upload_to=spending_request_document_path,
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
