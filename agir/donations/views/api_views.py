from django.http.response import JsonResponse
from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from agir.donations.serializers import (
    CreateDonationSerializer,
    SendDonationSerializer,
    TYPE_MONTHLY,
)
from agir.people.models import Person
from django.db import transaction
from agir.payments.actions.payments import create_payment
from agir.donations.allocations import create_monthly_donation
import json
from agir.donations.apps import DonsConfig
from agir.payments import payment_modes
from agir.payments.models import Subscription
from django.urls import reverse
from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.donations.tasks import send_monthly_donation_confirmation_email


class CreateDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CreateDonationSerializer
    queryset = Person.objects.none()


class SendDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SendDonationSerializer
    queryset = Person.objects.none()

    def clear_session(self):
        del self.request.session[DONATION_SESSION_NAMESPACE]

    # Create person with only its model fields in validated_data
    def create_person(self, validated_data):
        clean_data = {}
        for attr, value in validated_data.items():
            if getattr(Person, attr, False):
                clean_data[attr] = value

        person = Person.objects.create(**clean_data)
        person.save()
        return person

    def update_person(self, instance, validated_data):
        for attr, value in validated_data.items():
            # Add newsletters
            if attr == "subscribed_lfi":
                if Person.NEWSLETTER_LFI not in instance.newsletters:
                    instance.newsletters.append(Person.NEWSLETTER_LFI)
                continue
            if attr == "subscribed_2022":
                if Person.NEWSLETTER_2022 not in instance.newsletters:
                    instance.newsletters.append(Person.NEWSLETTER_2022)
                if Person.NEWSLETTER_2022_EXCEPTIONNEL not in instance.newsletters:
                    instance.newsletters.append(Person.NEWSLETTER_2022_EXCEPTIONNEL)
                continue
            setattr(instance, attr, value)
        instance.save()
        return instance

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        amount = validated_data["amount"]
        payment_mode = validated_data["payment_mode"]

        connected_user = False
        person = None

        # Check user connected
        if request.user.is_authenticated and request.user.person is not None:
            if validated_data["email"] == request.user.person.email:
                connected_user = True
                del validated_data["email"]

        # User exist and connected : update user informations
        if connected_user:
            person = Person.objects.get(pk=request.user.person.id)
            # Update newsletters only if checked
            if not validated_data["subscribed_lfi"]:
                del validated_data["subscribed_lfi"]

            if not validated_data["subscribed_2022"]:
                del validated_data["subscribed_2022"]

            self.update_person(person, validated_data)

        allocations = {
            str(allocation["group"].id): allocation["amount"]
            for allocation in validated_data.get("allocations", [])
        }

        if "allocations" in validated_data:
            validated_data["allocations"] = json.dumps(allocations)

        payment_type = DonsConfig.PAYMENT_TYPE

        # Monthly payments
        if validated_data["type"] == TYPE_MONTHLY:
            payment_type = DonsConfig.SUBSCRIPTION_TYPE

            # Confirm email if the user is unknowed
            if not connected_user:
                email = validated_data["email"]
                del validated_data["email"]
                send_monthly_donation_confirmation_email.delay(
                    confirmation_view_name="monthly_donation_confirm",
                    email=email,
                    subscription_total=amount,
                    **validated_data,
                )
                self.clear_session()
                return JsonResponse(
                    {"next": reverse("monthly_donation_confirmation_email_sent")}
                )

            # Check user already monthly donator
            if Subscription.objects.filter(
                person=person, status=Subscription.STATUS_ACTIVE, mode=payment_mode,
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
                return JsonResponse({"next": reverse("already_has_subscription")})

            with transaction.atomic():
                subscription = create_monthly_donation(
                    person=person,
                    mode=payment_mode,
                    subscription_total=amount,
                    allocations=allocations,
                    meta=validated_data,
                    type=payment_type,
                )

            self.clear_session()
            return JsonResponse(
                {"next": reverse("subscription_page", args=[subscription.pk])}
            )

        # Direct payments
        with transaction.atomic():
            payment = create_payment(
                person=person,
                type=payment_type,
                mode=payment_mode,
                price=amount,
                meta=validated_data,
                **kwargs,
            )

        self.clear_session()
        return JsonResponse({"next": payment.get_payment_url()})
