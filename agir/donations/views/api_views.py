import json

from django.db import transaction
from django.urls import reverse
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response

from agir.donations.serializers import (
    DonationSerializer,
    MONTHLY,
)
from agir.donations.tasks import send_monthly_donation_confirmation_email
from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.lib.rest_framework_permissions import IsActionPopulaireClientPermission
from agir.payments.actions.payments import create_payment
from agir.payments.actions.subscriptions import create_subscription
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

    def make_subscription(self):
        validated_data = self.validated_data
        payment_type = validated_data.get("payment_type")
        payment_mode = validated_data.get("payment_mode")
        amount = validated_data.get("amount")
        allocations = validated_data.get("allocations", [])
        end_date = validated_data.get("end_date")

        # Confirm email if the user is unknown
        if self.person is None:
            email = validated_data.pop("email", None)

            if not "allocations" in validated_data:
                validated_data["allocations"] = "[]"

            confirmation_view_name = "monthly_donation_confirm"

            send_monthly_donation_confirmation_email.delay(
                confirmation_view_name=confirmation_view_name,
                email=email,
                **validated_data,
            )
            self.clear_session()

            return Response(
                {"next": reverse("monthly_donation_confirmation_email_sent")}
            )

        existing_subscription = Subscription.objects.filter(
            person=self.person,
            status=Subscription.STATUS_ACTIVE,
            mode=payment_mode,
        ).first()

        # TODO: handle renewals from september on if existing_subscription is a contribution

        # Redirect if user already monthly donator
        if existing_subscription is not None:
            # stocker toutes les infos en session
            # attention à ne pas juste modifier le dictionnaire existant,
            # parce que la session ne se "rendrait pas compte" qu'elle a changé
            # et cela ne serait donc pas persisté
            self.request.session[DONATION_SESSION_NAMESPACE] = {
                "new_subscription": {
                    "from_type": existing_subscription.type,
                    "type": payment_type,
                    "mode": payment_mode,
                    "amount": amount,
                    "meta": validated_data,
                    "end_date": end_date,
                },
                **self.request.session.get(DONATION_SESSION_NAMESPACE, {}),
            }

            return Response({"next": reverse("already_has_subscription")})

        with transaction.atomic():
            subscription = create_subscription(
                person=self.person,
                type=payment_type,
                mode=payment_mode,
                amount=amount,
                allocations=allocations,
                meta=validated_data,
                end_date=end_date,
            )

        self.clear_session()
        return Response({"next": reverse("subscription_page", args=[subscription.pk])})

    def make_payment(self):
        payment_type = self.validated_data.get("payment_type")
        payment_mode = self.validated_data.get("payment_mode")
        amount = self.validated_data.get("amount")

        with transaction.atomic():
            payment = create_payment(
                person=self.person,
                type=payment_type,
                mode=payment_mode,
                price=amount,
                meta=self.validated_data,
                **self.kwargs,
            )

        self.clear_session()
        return Response({"next": payment.get_payment_url()})

    def post(self, request, *args, **kwargs):
        self.person = self.get_object()
        serializer = self.get_serializer(self.person, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data

        # User exist and connected : update user informations
        if self.person is not None:
            self.perform_update(serializer)

        if "allocations" in self.validated_data:
            self.validated_data["allocations"] = json.dumps(
                self.validated_data["allocations"]
            )

        if self.validated_data["payment_timing"] == MONTHLY:
            return self.make_subscription()

        return self.make_payment()
