import reversion
from django.conf import settings
from django.core import validators
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import empty

from agir.checks import DonationCheckPaymentMode
from agir.donations.actions import (
    can_make_contribution,
    get_end_date_from_datetime,
    monthly_to_single_time_contribution,
)
from agir.donations.apps import DonsConfig
from agir.donations.models import AllocationModelMixin, SpendingRequest, Document
from agir.donations.spending_requests import (
    get_spending_request_field_label,
    get_spending_request_field_labels,
    get_current_action,
)
from agir.donations.validators import IBANSerializerValidator, BICSerializerValidator
from agir.events.models import Event
from agir.events.serializers import EventListSerializer
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupSerializer
from agir.lib.data import departements_choices
from agir.lib.display import display_price
from agir.lib.serializers import PhoneField, CurrentPersonField
from agir.payments import payment_modes
from agir.people.models import Person

SINGLE_TIME = "S"
MONTHLY = "M"

SINGLE_TIME_PAYMENT_MODES = (payment_modes.DEFAULT_MODE, DonationCheckPaymentMode.id)
MONTHLY_PAYMENT_MODES = (payment_modes.DEFAULT_MODE,)


class DonationAllocationSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=AllocationModelMixin.TYPE_CHOICES,
        default=AllocationModelMixin.TYPE_GROUP,
        required=False,
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=SupportGroup.objects.active().certified(), required=False
    )
    departement = serializers.ChoiceField(choices=departements_choices, required=False)
    amount = serializers.IntegerField(min_value=1, required=True)

    def validate(self, attrs):
        if attrs.get("group"):
            attrs["group"] = str(attrs["group"].id)

        if attrs.get("type") == AllocationModelMixin.TYPE_GROUP and not attrs.get(
            "group"
        ):
            raise serializers.ValidationError(
                detail={
                    "group": "L'id du groupe est obligatoire pour ce type d'allocation"
                }
            )

        if attrs.get("type") == AllocationModelMixin.TYPE_DEPARTEMENT and not attrs.get(
            "departement"
        ):
            raise serializers.ValidationError(
                detail={
                    "departement": "Le code du departement est obligatoire pour ce type d'allocation"
                }
            )

        return attrs


class DonationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    firstName = serializers.CharField(max_length=255, source="first_name")
    lastName = serializers.CharField(max_length=255, source="last_name")
    gender = serializers.CharField()
    locationAddress1 = serializers.CharField(max_length=100, source="location_address1")
    locationAddress2 = serializers.CharField(
        max_length=100, source="location_address2", required=False, allow_blank=True
    )
    locationCity = serializers.CharField(max_length=100, source="location_city")
    locationZip = serializers.CharField(max_length=20, source="location_zip")
    locationCountry = serializers.CharField(max_length=100, source="location_country")
    contactPhone = PhoneField(max_length=30, required=True, source="contact_phone")
    nationality = serializers.CharField(max_length=100)

    to = serializers.ChoiceField(
        choices=(
            (DonsConfig.SINGLE_TIME_DONATION_TYPE, "don à la France insoumise"),
            (DonsConfig.CONTRIBUTION_TYPE, "contribution à la France insoumise"),
        ),
        default=DonsConfig.SINGLE_TIME_DONATION_TYPE,
        source="payment_type",
    )
    amount = serializers.IntegerField(required=True)
    endDate = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
        source="end_date",
    )
    paymentMode = serializers.CharField(max_length=20, source="payment_mode")
    paymentTiming = serializers.ChoiceField(
        source="payment_timing",
        choices=((SINGLE_TIME, "une seule fois"), (MONTHLY, "tous les mois")),
    )
    allocations = serializers.ListField(
        child=DonationAllocationSerializer(),
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    def validate_email(self, value):
        if self.instance is None and value is None:
            raise serializers.ValidationError("L'email est obligatoire.")
        return value

    def validate_end_date(self, value):
        if value is None:
            return value
        now = timezone.now().date()
        if value > now:
            return value
        raise serializers.ValidationError(
            "La date de fin de paiement est une date passée"
        )

    def validate_allocation_amount(self, attrs):
        allocations = attrs.get("allocations")
        if allocations:
            amount = attrs.get("amount")
            total_allocations = sum(
                [allocation.get("amount", 0) for allocation in allocations]
            )
            if total_allocations > amount:
                raise serializers.ValidationError(
                    detail={
                        "global": "La somme des montants des allocations est supérieur au montant total"
                    }
                )

        return attrs

    def validate_amount_range(self, attrs):
        amount = attrs.get("amount")
        payment_timing = attrs.get("payment_timing")
        error = None
        mininimum = settings.DONATION_MINIMUM
        maximum = settings.DONATION_MAXIMUM

        if payment_timing == MONTHLY:
            mininimum = settings.MONTHLY_DONATION_MINIMUM
            maximum = settings.MONTHLY_DONATION_MAXIMUM

        if amount > maximum:
            error = f"Le montant maximum autorisé est de {display_price(maximum)}."
        elif amount < mininimum:
            error = (
                f"Le montant ne peut pas être inférieur à {display_price(mininimum)}."
            )

        if error:
            raise serializers.ValidationError(detail={"global": error})

        return attrs

    def validate_lfi_donations(self, attrs):
        payment_mode = attrs["payment_mode"]
        error = False

        if attrs["payment_timing"] == MONTHLY:
            if payment_mode not in MONTHLY_PAYMENT_MODES:
                error = True
        elif attrs["payment_timing"] == SINGLE_TIME:
            if payment_mode not in SINGLE_TIME_PAYMENT_MODES:
                error = True

        if error:
            raise serializers.ValidationError(
                detail={
                    "global": "Ce mode de paiement n'est actuellement pas autorisé pour ce type de dons."
                }
            )
        return attrs

    def validate_lfi_contributions(self, attrs):
        if not can_make_contribution(email=attrs.get("email")):
            raise serializers.ValidationError(
                detail={
                    "global": "Merci de votre soutien, mais vous avez déjà fait une contribution pour cette année !"
                }
            )

        payment_mode = attrs.get("payment_mode")

        attrs["end_date"] = get_end_date_from_datetime(attrs["end_date"])

        if payment_mode not in MONTHLY_PAYMENT_MODES:
            # Force single time payment for checks and update amounts
            attrs = monthly_to_single_time_contribution(attrs)
            attrs["payment_timing"] = SINGLE_TIME
        else:
            # Force monthly payment for system pay
            attrs["payment_timing"] = MONTHLY

        return attrs

    def validate(self, attrs):
        attrs["location_state"] = attrs.get("location_country")

        payment_type = attrs.get("payment_type")

        if payment_type == DonsConfig.CONTRIBUTION_TYPE:
            attrs = self.validate_lfi_contributions(attrs)
        elif payment_type == DonsConfig.SINGLE_TIME_DONATION_TYPE:
            attrs = self.validate_lfi_donations(attrs)

        attrs = self.validate_amount_range(attrs)
        attrs = self.validate_allocation_amount(attrs)

        return attrs

    def save(self, **kwargs):
        validated_data = self.validated_data

        if self.instance is not None and "email" in validated_data:
            del validated_data["email"]

        super().save(**validated_data)

    class Meta:
        model = Person
        fields = (
            "email",
            "firstName",
            "lastName",
            "gender",
            "locationAddress1",
            "locationAddress2",
            "locationCity",
            "locationZip",
            "locationCountry",
            "contactPhone",
            "nationality",
            "to",
            "amount",
            "endDate",
            "paymentMode",
            "paymentTiming",
            "allocations",
        )


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(
        source="contact_name",
        label="Nom du contact",
        max_length=255,
    )
    email = serializers.EmailField(
        source="contact_email",
        label="Adresse email du contact",
        required=False,
        allow_blank=True,
    )
    phone = PhoneField(
        source="contact_phone",
        label="Numéro de téléphone du contact",
        max_length=30,
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.setdefault("source", "*")
        super().__init__(instance, data, **kwargs)


class IBANSerializer(serializers.CharField):
    default_validators = [IBANSerializerValidator]


class BICSerializer(serializers.CharField):
    default_validators = [BICSerializerValidator]


class BankAccountSerializer(serializers.Serializer):
    name = serializers.CharField(
        source="bank_account_name",
        label="Nom du contact",
        max_length=255,
    )
    iban = IBANSerializer(source="bank_account_iban", label="IBAN")
    bic = BICSerializer(source="bank_account_bic", label="BIC")
    rib = serializers.FileField(
        source="bank_account_rib",
        label="RIB",
        validators=[validators.FileExtensionValidator(["pdf", "png", "jpeg", "jpg"])],
        required=False,
        allow_null=True,
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.setdefault("source", "*")
        super().__init__(instance, data, **kwargs)


class SpendingRequestDocumentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(label="Identifiant", read_only=False, required=False)
    file = serializers.FileField(
        label="Fichier", allow_null=False, allow_empty_file=False, required=True
    )
    request = serializers.PrimaryKeyRelatedField(
        label="Demande de dépense",
        queryset=SpendingRequest.objects.all(),
        write_only=True,
        required=False,
    )

    def create(self, validated_data):
        with reversion.create_revision():
            validated_data.pop("id", None)
            reversion.set_user(self.context["request"].user)
            reversion.set_comment(f"Ajout d'une pièce-jointe")
            return super().create(validated_data)

    def update(self, instance, validated_data):
        # Set request only upon creation
        validated_data.pop("request", None)
        with reversion.create_revision():
            reversion.set_user(self.context["request"].user)
            reversion.set_comment(f"Mise à jour d'une pièce-jointe")
            return super().update(instance, validated_data)

    class Meta:
        model = Document
        fields = ("id", "title", "type", "file", "request")


class SpendingRequestVersionSerializer(serializers.Serializer):
    id = serializers.CharField()
    modified = serializers.DateTimeField()
    person = serializers.SerializerMethodField()
    title = serializers.CharField()
    comment = serializers.CharField()
    diff = serializers.ListField()

    def get_person(self, obj):
        person = obj and obj.get("person")

        if not person:
            return None

        if not isinstance(person, Person):
            return person

        return {
            "id": person.id,
            "displayName": person.display_name,
            "gender": person.gender,
            "image": person.image.thumbnail.url
            if (person.image and person.image.thumbnail)
            else None,
        }


class SpendingRequestSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(label="Identifiant")
    created = serializers.ReadOnlyField(label="Date de création")
    modified = serializers.ReadOnlyField(label="Dernière modification")
    status = serializers.ReadOnlyField(label="Statut", source="get_status_display")
    groupId = serializers.PrimaryKeyRelatedField(
        source="group",
        label="Groupe d'action",
        queryset=SupportGroup.objects.active(),
        write_only=True,
    )
    group = SupportGroupSerializer(read_only=True, fields=("id", "name"))
    category = serializers.ChoiceField(
        label="Catégorie", choices=SpendingRequest.Category.visible_choices
    )
    eventId = serializers.PrimaryKeyRelatedField(
        source="event",
        label="Événement lié à la dépense",
        queryset=Event.objects.public(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    event = EventListSerializer(
        read_only=True,
        fields=(
            "id",
            "name",
            "illustration",
            "startTime",
            "endTime",
            "location",
            "rsvp",
            "subtype",
        ),
    )
    spendingDate = serializers.DateField(source="spending_date")
    contact = ContactSerializer(required=True)
    bankAccount = BankAccountSerializer(required=True)
    attachments = SpendingRequestDocumentSerializer(many=True, required=False)
    comment = serializers.CharField(
        label="Commentaire", required=False, write_only=True
    )
    history = SpendingRequestVersionSerializer(
        label="Historique", source="get_history", read_only=True, many=True
    )
    action = serializers.SerializerMethodField(read_only=True)

    def get_action(self, spending_request):
        return get_current_action(spending_request, self.context["request"].user)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save_attachments(self, validated_data, spending_request):
        errors = []
        for i, document in enumerate(validated_data):
            document["request"] = spending_request.id
            document_id = document.get("id", None)
            instance = spending_request.documents.filter(id=document_id).first()
            partial = self.partial and instance is not None
            serializer = SpendingRequestDocumentSerializer(
                instance, data=document, partial=partial, context=self.context
            )
            try:
                serializer.is_valid(raise_exception=True)
            except serializers.ValidationError as e:
                errors.append([i, e.detail])
            else:
                serializer.save()

        if errors:
            raise serializers.ValidationError(detail={"attachments": errors})

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user.person
        reversion.set_comment("Création de la demande")
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Set group only upon creation
        validated_data.pop("group", None)
        return super().update(instance, validated_data)

    def save(self, **kwargs):
        comment = self.validated_data.pop("comment", "Mise à jour de la demande")
        attachments = self.validated_data.pop("attachments", [])

        with reversion.create_revision(atomic=True):
            reversion.set_user(self.context["request"].user)
            reversion.set_comment(comment)
            spending_request = super().save(**kwargs)
            reversion.is_manage_manually()

            if attachments:
                self.save_attachments(attachments, spending_request)

            return spending_request

    class Meta:
        model = SpendingRequest
        fields = (
            "id",
            "created",
            "modified",
            "title",
            "campaign",
            "amount",
            "status",
            "groupId",
            "group",
            "category",
            "explanation",
            "eventId",
            "event",
            "spendingDate",
            "contact",
            "bankAccount",
            "attachments",
            "editable",
            "deletable",
            "comment",
            "history",
            "action",
        )
