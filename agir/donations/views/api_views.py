import json

from django.db import transaction
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response

from agir.donations.allocations import create_monthly_donation
from agir.donations.apps import DonsConfig
from agir.donations.serializers import (
    DonationSerializer,
    TYPE_MONTHLY,
)
from agir.donations.tasks import send_monthly_donation_confirmation_email
from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.lib.rest_framework_permissions import IsActionPopulaireClientPermission
from agir.payments.actions.payments import create_payment
from agir.payments.models import Subscription


class CreateDonationAPIView(UpdateModelMixin, GenericAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    serializer_class = DonationSerializer

    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user.person

    def clear_session(self):
        if DONATION_SESSION_NAMESPACE in self.request.session:
            del self.request.session[DONATION_SESSION_NAMESPACE]

    def monthly_payment(self, allocations):
        validated_data = self.validated_data
        payment_mode = validated_data["payment_mode"]
        amount = validated_data["amount"]
        payment_type = DonsConfig.SUBSCRIPTION_TYPE

        # Confirm email if the user is unknown
        if self.person is None:
            email = validated_data.pop("email", None)

            if not "allocations" in validated_data:
                validated_data["allocations"] = "[]"

            confirmation_view_name = "monthly_donation_confirm"

            send_monthly_donation_confirmation_email.delay(
                confirmation_view_name=confirmation_view_name,
                email=email,
                subscription_total=amount,
                **validated_data,
            )
            self.clear_session()
            return Response(
                {"next": reverse("monthly_donation_confirmation_email_sent")}
            )

        # Redirect if user already monthly donator
        if Subscription.objects.filter(
            person=self.person,
            status=Subscription.STATUS_ACTIVE,
            mode=payment_mode,
        ):
            # stocker toutes les infos en session
            # attention à ne pas juste modifier le dictionnaire existant,
            # parce que la session ne se "rendrait pas compte" qu'elle a changé
            # et cela ne serait donc pas persisté
            self.request.session[DONATION_SESSION_NAMESPACE] = {
                "new_subscription": {
                    "type": payment_type,
                    "mode": payment_mode,
                    "subscription_total": amount,
                    "meta": validated_data,
                },
                **self.request.session.get(DONATION_SESSION_NAMESPACE, {}),
            }
            return Response({"next": reverse("already_has_subscription")})

        with transaction.atomic():
            subscription = create_monthly_donation(
                person=self.person,
                mode=payment_mode,
                subscription_total=amount,
                allocations=allocations,
                meta=validated_data,
                type=payment_type,
            )

        self.clear_session()
        return Response({"next": reverse("subscription_page", args=[subscription.pk])})

    def post(self, request, *args, **kwargs):

        self.person = self.get_object()
        serializer = self.get_serializer(self.person, data=request.data)
        serializer.is_valid(raise_exception=True)

        self.validated_data = serializer.validated_data
        validated_data = self.validated_data
        amount = validated_data["amount"]
        payment_mode = validated_data["payment_mode"]

        # User exist and connected : update user informations
        if self.person is not None:
            self.perform_update(serializer)

        # TODO: new allocation format and types should be handled here:
        allocations = {
            str(allocation["group"].id): allocation["amount"]
            for allocation in validated_data.get("allocations", [])
            if "group" in allocation
        }

        if "allocations" in validated_data:
            validated_data["allocations"] = json.dumps(allocations)

        # Monthly payments
        if validated_data["payment_timing"] == TYPE_MONTHLY:
            return self.monthly_payment(allocations)

        # Direct payments
        payment_type = DonsConfig.PAYMENT_TYPE

        validated_data["location_state"] = validated_data["location_country"]

        with transaction.atomic():
            payment = create_payment(
                person=self.person,
                type=payment_type,
                mode=payment_mode,
                price=amount,
                meta=validated_data,
                **kwargs,
            )

        self.clear_session()
        return Response({"next": payment.get_payment_url()})
