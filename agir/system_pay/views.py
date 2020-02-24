import logging

from django.db import transaction
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from rest_framework import serializers
from rest_framework.views import APIView

from agir.payments.actions import subscriptions
from agir.payments.actions.payments import notify_status_change, create_payment
from agir.payments.actions.subscriptions import (
    notify_status_change as notify_subscription_status_change,
)
from agir.system_pay.actions import (
    update_payment_from_transaction,
    update_subscription_from_transaction,
    replace_sp_subscription_for_subscription,
)
from agir.system_pay.models import (
    SystemPayTransaction,
    SystemPayAlias,
    SystemPaySubscription,
)
from agir.system_pay.serializers import SystemPayWebhookSerializer
from .forms import SystempayPaymentForm, SystempayNewSubscriptionForm

logger = logging.getLogger(__name__)

SYSTEMPAY_STATUS_CHOICE = {
    "ABANDONED": SystemPayTransaction.STATUS_ABANDONED,
    "CANCELED": SystemPayTransaction.STATUS_CANCELED,
    "REFUSED": SystemPayTransaction.STATUS_REFUSED,
    "AUTHORISED": SystemPayTransaction.STATUS_COMPLETED,
    "AUTHORISED_TO_VALIDATE": SystemPayTransaction.STATUS_COMPLETED,
    "ACCEPTED": SystemPayTransaction.STATUS_COMPLETED,
    "CAPTURED": SystemPayTransaction.STATUS_COMPLETED,
}
SYSTEMPAY_OPERATION_TYPE_CHOICE = ["DEBIT", "CREDIT", "VERIFICATION"]
PAYMENT_ID_SESSION_KEY = "_payment_id"
SUBSCRIPTION_ID_SESSION_KEY = "_payment_id"


class BaseSystemPayRedirectView(TemplateView):
    template_name = "system_pay/redirect.html"
    sp_config = None


class SystempayRedirectView(BaseSystemPayRedirectView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=SystempayPaymentForm.get_form_for_transaction(
                self.transaction, self.sp_config
            ),
            **kwargs,
        )

    @never_cache
    def get(self, request, *args, **kwargs):
        self.payment = kwargs["payment"]
        self.transaction = SystemPayTransaction.objects.create(payment=self.payment)
        res = super().get(request, *args, **kwargs)

        return res


class SystemPaySubscriptionRedirectView(BaseSystemPayRedirectView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=SystempayNewSubscriptionForm.get_form_for_transaction(
                self.transaction, self.sp_config
            ),
            **kwargs,
        )

    def get(self, request, *args, **kwargs):
        self.subscription = kwargs["subscription"]
        self.transaction = SystemPayTransaction.objects.create(
            subscription=self.subscription
        )
        res = super().get(request, *args, **kwargs)

        # save payment in session
        request.session[SUBSCRIPTION_ID_SESSION_KEY] = self.subscription.pk

        return res


class SystemPayWebhookView(APIView):
    permission_classes = []
    sp_config = None
    mode_id = None

    def post(self, request):
        # La requête transmise par SystemPay comprend deux identifiants :
        # - vads_order_id : Identifie la "commande". Plusieurs transactions
        #   SystemPay vont partager le numéro de "commande" lorsqu'elles sont
        #   logiquement liées entre elles : c'est le cas par exemple d'une
        #   transaction de paiement et d'une transaction de remboursement
        #   subséquente, ou de toutes les transactions liées à une souscription.
        # - vads_trans_id : Identifie la transaction elle-même. Il s'agit
        #   d'un identifiant assez court, et il n'est pas unique : SystemPay
        #   ne demande d'unicité que sur la journée.
        # - vads_trans_uuid: Identifiant universellement unique qui identifie
        #   la transaction. Créé par SystemPay, qui nous le communique.
        #
        # Les numéros de commande sont toujours choisis par nous :
        # - pour les paiements, le numéro de commande est l'id interne de la
        #   transaction SystemPay (il s'agit d'un identifiant automatique dans
        #   psql). Les éventuels remboursements reprennent ce numéro de commande.
        # - pour une souscription, il s'agit de l'identifiant de la transaction
        #   qui la confirme. Les transactions mensuelles subséquentes reprennent
        #   ce numéro de commande. Pour les souscriptions créées via l'API, le
        #   numéro de commande est choisi explicitement à ce moment-là.
        #
        # Pour les numéros de transaction, deux cas se présentent :
        # - pour les transactions que nous créons nous-mêmes, le numéro de
        #   transaction correspond à un troncage de l'identifiant interne
        #   de la transaction.
        # - pour les transactions de remboursement et celles de souscriptions,
        #   le numéro n'est pas choisi par nous mais par SystemPay.
        #
        # En pratique, nous n'utilisons pas les ID de transaction pour le moment.

        serializer = SystemPayWebhookSerializer(
            sp_config=self.sp_config, data=request.data
        )

        # le serializer permet de valider à la fois la signature et la structure générale
        # de la requête.
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            logger.exception(
                "Contenu de la transaction invalide", extra={"request": request}
            )

            # on reraise pour s'assurer que SystemPay reçoit une réponse en 4xx
            raise

        # on vérifie, pour garantir l'idempotence, que la transaction n'a pas déjà été
        # traitée, en cherchant une transaction de même UUID. Même dans le cas des paiements,
        # où la transaction existe déjà, nous n'avons pas encore son UUID (qui est généré côté
        # SystemPay) et nous ne devrions donc pas trouver de transaction.
        try:
            sp_transaction = serializer.get_transaction_by_uuid()
        except serializers.ValidationError:
            # Aucune transaction avec cette UUID n'est connue, ce qui est attendu !
            pass
        else:
            # Transaction déjà traitée ! On vérifie que l'appel précédent avait exactement les mêmes
            # arguments, parce que sinon c'est bizarre
            if sp_transaction.webhook_calls and serializer.is_identical(
                sp_transaction.webhook_calls[-1]
            ):
                return self.successful_response()
            else:
                # Dans le cas où c'est un contenu différent, on vérifie que c'est bien un retry
                if serializer.data.get("url_check_src") != "RETRY":
                    logger.error(
                        f"Webhook appelé deux fois différemment pour la même transaction",
                        extra={"request": request},
                    )
                    raise serializers.ValidationError(
                        detail="Webhook appelé deux fois différemment pour la même transaction",
                        code="duplicate_webhook",
                    )

        operation_type = serializer.data.get("vads_operation_type")

        try:
            with transaction.atomic():
                if operation_type == "CREDIT":
                    return self.handle_refund(serializer)
                elif operation_type == "VERIFICATION":
                    return self.handle_subscription(serializer)
                else:
                    return self.handle_payment(serializer)
        except serializers.ValidationError:
            logger.exception(
                "Erreur lors du traitement d'une transaction",
                extra={"request": request},
            )

            # on lance l'exception de nouveau pour s'assurer que SystemPay reçoit une réponse en 4xx
            raise

    def successful_response(self):
        return HttpResponse({"status": "Accepted"}, 200)

    def save_transaction(self, sp_transaction, serializer):
        """Sauvegarde le contenu de l'appel webhook ainsi que status et uuid de la transaction

        :param sp_transaction:
        :param serializer:
        :return:
        """
        # sauve les données nettoyées (i.e. les champs sensibles et superflus sont retirés)
        sp_transaction.webhook_calls.append(serializer.cleaned_data)
        sp_transaction.status = serializer.validated_data["trans_status"]
        sp_transaction.uuid = serializer.validated_data.get("trans_uuid")
        sp_transaction.save()

    def handle_refund(self, serializer):
        # dans le cas d'un remboursement, l'order_id est l'id de la transaction d'origine
        original_sp_transaction = serializer.get_transaction_by_order_id()
        payment = original_sp_transaction.payment

        if payment is None:
            raise serializers.ValidationError(
                "pas de paiement associé à la transaction d'origine",
                code="missing_payment",
            )

        if payment.mode != self.mode_id:
            raise serializers.ValidationError(
                "le mode du paiement ne correspond pas à celui pour lequel le webhook est défini",
                code="wrong_mode",
            )

        # N.B.: on accepte que les remboursements complets
        serializer.check_payment_match_transaction(payment)

        sp_transaction = SystemPayTransaction.objects.get_or_create(
            uuid=serializer.validated_data["vads_trans_uuid"],
            defaults={"payment": payment, "is_refund": True},
        )

        self.save_transaction(sp_transaction, serializer)

        update_payment_from_transaction(payment, sp_transaction)
        notify_status_change(payment)

        return self.successful_response()

    def handle_payment(self, serializer):
        subscription_id = serializer.validated_data.get("subscription")

        if subscription_id:
            # il s'agit d'un paiement automatique lié à une souscription
            # on devrait avoir la trace de cette souscription dans notre
            # base de données
            sp_subscription = serializer.get_sp_subscription()
            subscription = sp_subscription.subscription

            if subscription.mode != self.mode_id:
                raise serializers.ValidationError(
                    "le mode du paiement ne correspond pas à celui pour lequel le webhook est défini",
                    code="wrong_mode",
                )

            serializer.check_and_update_alias(sp_subscription.alias)
            serializer.check_subscription_match_transaction(subscription)

            if subscription.person is None:
                # si la personne n'existe plus, il y a un problème, on met fin à la souscription
                subscriptions.terminate_subscription(subscription)
                logger.error(
                    "Paiement automatique déclenché par SystemPay sur une transaction sans personne "
                    "associée. Par sécurité, la subscription a été terminée."
                )

            payment = create_payment(
                person=subscription.person,
                type=subscription.type,
                price=serializer.validated_data["amount"],
                mode=self.mode_id,
                subscription=subscription,
            )

            sp_transaction = SystemPayTransaction(
                payment=payment, alias=sp_subscription.alias, is_refund=False
            )

        else:
            # dans ce cas il s'agit d'un paiement via le formulaire
            sp_transaction = serializer.get_transaction_by_order_id()
            payment = sp_transaction.payment

            if payment is None:
                raise serializers.ValidationError(
                    "pas de paiement associé à la transaction", code="missing_payment"
                )

            if payment.mode != self.mode_id:
                raise serializers.ValidationError(
                    "le mode du paiement ne correspond pas à celui pour lequel le webhook est défini",
                    code="wrong_mode",
                )

        self.save_transaction(sp_transaction, serializer)
        update_payment_from_transaction(payment, sp_transaction)
        notify_status_change(payment)

        return self.successful_response()

    def handle_subscription(self, serializer):
        sp_transaction = serializer.get_transaction_by_order_id()

        if sp_transaction.subscription is None:
            raise serializers.ValidationError(
                "Souscription manquante sur la transaction", code="missing_subscription"
            )

        if sp_transaction.subscription.mode != self.mode_id:
            raise serializers.ValidationError(
                "le mode de la souscription ne correspond pas à celui pour lequel le webhook est défini",
                code="wrong_mode",
            )

        if serializer.is_successful():
            # Création ou récupération de l'alias (normalement il s'agit d'un nouveau)
            alias, created = SystemPayAlias.objects.get_or_create(
                identifier=serializer.validated_data["identifier"],
                defaults={"expiry_date": serializer.validated_data["expiry_date"]},
            )
            if not created:
                serializer.check_and_update_alias(alias)

            # création de la souscription SystemPay correspondante
            # (pour relier, alias, souscription et identifiant de souscription)
            sp_subscription, created = SystemPaySubscription.objects.get_or_create(
                identifier=serializer.validated_data["subscription"],
                subscription=sp_transaction.subscription,
                alias=alias,
            )

            replace_sp_subscription_for_subscription(
                sp_transaction.subscription, sp_subscription
            )

        self.save_transaction(sp_transaction, serializer)

        update_subscription_from_transaction(
            sp_transaction.subscription, sp_transaction
        )

        notify_subscription_status_change(sp_transaction.subscription)

        return self.successful_response()


def failure_view(request, pk):
    try:
        sp_transaction = SystemPayTransaction.objects.get(pk=pk)
    except SystemPayTransaction.DoesNotExist:
        raise Http404("Cette page n'existe pas.")

    status = request.GET.get("status", "unknown")

    if sp_transaction.payment is None and sp_transaction.subscription is None:
        logger.error(
            "Retour de SystemPay sans paiement ni souscription",
            extra={"request": request, "sp_transaction": sp_transaction},
        )
        raise ValueError("SystemPayTransaction sans paiement ni souscription")

    if sp_transaction.payment:
        retry_url = reverse("payment_retry", kwargs={"pk": sp_transaction.payment_id})
        return TemplateResponse(
            request,
            "system_pay/payment_failed.html",
            context={"retry_url": retry_url, "status": status},
        )
    else:
        retry_url = reverse(
            "subscription_page", kwargs={"pk": sp_transaction.subscription_id}
        )
        return TemplateResponse(
            request,
            "system_pay/subscription_failed.html",
            context={"retry_url": retry_url, "status": status},
        )
