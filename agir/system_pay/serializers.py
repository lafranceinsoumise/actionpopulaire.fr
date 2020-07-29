from datetime import date

import calendar
from uuid import UUID

from rest_framework import serializers

from agir.payments.models import Subscription
from agir.system_pay.crypto import check_signature
from agir.system_pay.models import SystemPayTransaction, SystemPaySubscription
from agir.system_pay.utils import clean_system_pay_data

SYSTEMPAY_OPERATION_TYPE_CHOICE = ["DEBIT", "CREDIT", "VERIFICATION"]
SYSTEMPAY_STATUS_CHOICE = {
    "ABANDONED": SystemPayTransaction.STATUS_ABANDONED,
    "CANCELED": SystemPayTransaction.STATUS_CANCELED,
    "REFUSED": SystemPayTransaction.STATUS_REFUSED,
    "AUTHORISED": SystemPayTransaction.STATUS_COMPLETED,
    "AUTHORISED_TO_VALIDATE": SystemPayTransaction.STATUS_COMPLETED,
    "ACCEPTED": SystemPayTransaction.STATUS_COMPLETED,
    "CAPTURED": SystemPayTransaction.STATUS_COMPLETED,
}


class SystemPayWebhookSerializer(serializers.Serializer):
    vads_order_id = serializers.CharField(required=True, source="order_id")
    vads_trans_uuid = serializers.UUIDField(
        required=False, source="trans_uuid"
    )  # absent pour les abandons
    vads_operation_type = serializers.ChoiceField(
        choices=SYSTEMPAY_OPERATION_TYPE_CHOICE, required=False, source="operation_type"
    )
    vads_trans_status = serializers.ChoiceField(
        choices=list(SYSTEMPAY_STATUS_CHOICE), required=True, source="trans_status"
    )
    vads_amount = serializers.IntegerField(required=False, source="amount")
    vads_cust_id = serializers.CharField(required=True, source="cust_id")

    vads_url_check_src = serializers.CharField(required=False, source="url_check_src")

    # information de l'alias
    vads_identifier = serializers.UUIDField(required=False, source="identifier")
    vads_expiry_year = serializers.IntegerField(required=False, source="expiry_year")
    vads_expiry_month = serializers.IntegerField(required=False, source="expiry_month")

    # information de la subscription
    vads_subscription = serializers.CharField(required=False, source="subscription")

    def __init__(self, sp_config, data=serializers.empty, **kwargs):
        super().__init__(instance=None, data=data)
        self.sp_config = sp_config

    def validate_vads_trans_status(self, value):
        return value and SYSTEMPAY_STATUS_CHOICE[value]

    def validate_vads_cust_id(self, value):
        if value == "anonymous":
            return None

        try:
            return UUID(value)
        except ValueError:
            raise serializers.ValidationError("bad vads_cust_id")

    def validate(self, validated_data):
        # On vérifie que la requête est correctement signée
        initial_data = self.initial_data
        self.cleaned_data = clean_system_pay_data(initial_data)

        if "signature" not in initial_data or not check_signature(
            initial_data, self.sp_config["certificate"]
        ):
            raise serializers.ValidationError(
                detail={"signature": "Signature manquante ou incorrecte"},
                code="bad_signature",
            )

        if validated_data.get("operation_type") is None:
            # on est probablement dans le cas d'une annulation
            if (
                validated_data.get("trans_status")
                != SystemPayTransaction.STATUS_ABANDONED
            ):
                raise serializers.ValidationError(
                    detail="Type d'opération manquant", code="missing_operation_type"
                )

            sp_transaction = self.get_transaction_by_order_id(
                validated_data.get("order_id")
            )

            if sp_transaction.subscription is not None:
                validated_data["operation_type"] = "VERIFICATION"
            elif sp_transaction.payment is not None:
                validated_data["operation_type"] = "DEBIT"
            else:
                raise serializers.ValidationError(
                    detail="Transaction dans un état incorrect", code="bad_transaction"
                )

        if validated_data.get("expiry_year") and validated_data.get("expiry_month"):
            validated_data["expiry_date"] = date(
                year=validated_data.get("expiry_year"),
                month=validated_data.get("expiry_month"),
                day=calendar.monthrange(
                    validated_data.get("expiry_year"),
                    validated_data.get("expiry_month"),
                )[1],
            )

        if validated_data.get(
            "operation_type"
        ) == "VERIFICATION" and self.is_successful(validated_data):
            if not validated_data.get("subscription"):
                raise serializers.ValidationError(
                    detail={
                        "subscription": "Identifiant de la subscription manquant pour une vérification réussie"
                    },
                    code="missing_subscription_id",
                )

            if (
                not validated_data.get("identifier")
                or not validated_data.get("expiry_year")
                or not validated_data.get("expiry_month")
            ):
                raise serializers.ValidationError(
                    detail={"identifier": "Information manquante sur l'alias"},
                    code="missing_alias",
                )

        if self.is_successful(validated_data) and "amount" not in validated_data:
            raise serializers.ValidationError(
                detail={"amount": "Montant d'une transaction réussie manquant"},
                code="missing_amount",
            )

        return validated_data

    def is_successful(self, validated_data=None):
        if validated_data is None:
            validated_data = self.validated_data
        return validated_data["trans_status"] == SystemPayTransaction.STATUS_COMPLETED

    def is_identical(self, log_data):
        retry_varying_data = ["vads_hash", "vads_url_check_src"]
        current_cleaned_data = {
            k: v for k, v in self.cleaned_data.items() if k not in retry_varying_data
        }
        log_data = {k: v for k, v in log_data.items() if k not in retry_varying_data}
        return current_cleaned_data == log_data

    def check_payment_match_transaction(self, payment):
        if payment is None:
            raise serializers.ValidationError(
                detail="Paiement inexistant", code="missing_payment"
            )

        if (
            payment.person is not None
            and payment.person.id != self.validated_data["cust_id"]
        ):
            raise serializers.ValidationError(
                detail="mauvaise personne", code="wrong_person"
            )
        if payment.price != self.validated_data["amount"]:
            raise serializers.ValidationError(
                detail="mauvais montant", code="wrong_amount"
            )

    def check_subscription_match_transaction(self, subscription):
        person = subscription.person
        if person is not None and person.id != self.validated_data["cust_id"]:
            raise serializers.ValidationError(
                detail="Personne différente pour la souscription", code="wrong_person"
            )

        if subscription.price != self.validated_data["amount"]:
            raise serializers.ValidationError(
                detail="mauvais montant", code="wrong_price"
            )

        if subscription.status != Subscription.STATUS_ACTIVE:
            raise serializers.ValidationError(
                detail="Souscription non active", code="inactive_subscription"
            )

    def check_and_update_alias(self, alias):
        if alias.identifier != self.validated_data["identifier"]:
            raise serializers.ValidationError(
                "Alias différent de celui prévu", code="wrong_alias"
            )

        # mise à jour de la date d'expiration de l'alias
        if "expiry_date" in self.validated_data:
            if alias.expiry_date != self.validated_data["expiry_date"]:
                alias.expiry_date = self.validated_data["expiry_date"]
                alias.save()

    def get_transaction_by_uuid(self):
        if "trans_uuid" not in self.validated_data:
            raise serializers.ValidationError(
                detail={"uuid": "Aucune transaction avec cet UUID"}, code="unknown_uuid"
            )

        try:
            return SystemPayTransaction.objects.get(
                uuid=self.validated_data["trans_uuid"]
            )
        except SystemPayTransaction.DoesNotExist:
            raise serializers.ValidationError(
                detail={"uuid": "Aucune transaction avec cet UUID"}, code="unknown_uuid"
            )

    def get_transaction_by_order_id(self, order_id=None):
        if order_id is None:
            order_id = self.validated_data["order_id"]
        try:
            return SystemPayTransaction.objects.get(pk=order_id)
        except SystemPayTransaction.DoesNotExist:
            raise serializers.ValidationError(
                detail={"order_id": "Aucune transaction avec cet order_id"},
                code="unknown_order_id",
            )

    def get_sp_subscription(self):
        try:
            return SystemPaySubscription.objects.select_related(
                "subscription__person", "alias"
            ).get(identifier=self.validated_data["subscription"])
        except SystemPaySubscription.DoesNotExist:
            raise serializers.ValidationError(
                "Souscription non trouvée", code="missing_subscription"
            )
