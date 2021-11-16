from django.http.response import JsonResponse
from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from agir.donations.serializers import (
    CreateDonationSessionSerializer,
    SendDonationSerializer,
    TO_2022,
    TYPE_MONTHLY,
)
from agir.people.models import Person
from django.db import transaction
from agir.payments.actions.payments import create_payment
from agir.donations.allocations import create_monthly_donation
import json
from agir.donations.apps import DonsConfig
from agir.payments.models import Subscription
from django.urls import reverse
from agir.donations.views import DONATION_SESSION_NAMESPACE
from agir.donations.tasks import send_monthly_donation_confirmation_email
from agir.presidentielle2022.apps import Presidentielle2022Config

# 1st step : Fill session with donation infos
class CreateSessionDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CreateDonationSessionSerializer
    queryset = Person.objects.none()


# 2nd step : Create and send donation with personal infos
class SendDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SendDonationSerializer
    queryset = Person.objects.none()

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.validated_data = serializer.validated_data
        self.connected_user = False

        # Check user connected
        if request.user.is_authenticated and request.user.person is not None:
            if self.validated_data["email"] == request.user.person.email:
                self.connected_user = True
                del self.validated_data["email"]

    def clear_session(self):
        del self.request.session[DONATION_SESSION_NAMESPACE]

    # Update person and add newsletters in validated_data
    def update_person(self, instance, validated_data):
        for attr, value in validated_data.items():
            # Add newsletters
            if attr == "subscribed_2022":
                if Person.NEWSLETTER_2022 not in instance.newsletters:
                    instance.newsletters.append(Person.NEWSLETTER_2022)
                if Person.NEWSLETTER_2022_EXCEPTIONNEL not in instance.newsletters:
                    instance.newsletters.append(Person.NEWSLETTER_2022_EXCEPTIONNEL)
                continue
            setattr(instance, attr, value)
        instance.save()
        return instance

    def monthly_payment(self, person, allocations):
        connected_user = self.connected_user
        validated_data = self.validated_data
        payment_mode = validated_data["payment_mode"]
        amount = validated_data["amount"]

        payment_type = DonsConfig.SUBSCRIPTION_TYPE
        if validated_data["to"] == TO_2022:
            payment_type = Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE

        # Confirm email if the user is unknown
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

    def post(self, request, *args, **kwargs):
        validated_data = self.validated_data
        amount = validated_data["amount"]
        payment_mode = validated_data["payment_mode"]
        person = None
        connected_user = self.connected_user

        # User exist and connected : update user informations
        if connected_user:
            person = Person.objects.get(pk=request.user.person.id)
            # Update newsletters and support only if checked
            if (
                "subscribed_2022" in validated_data
                and not validated_data["subscribed_2022"]
            ):
                del validated_data["subscribed_2022"]
            if "is_2022" in validated_data and not validated_data["is_2022"]:
                del validated_data["is_2022"]

            self.update_person(person, validated_data)

        allocations = {
            str(allocation["group"].id): allocation["amount"]
            for allocation in validated_data.get("allocations", [])
        }

        if "allocations" in validated_data:
            validated_data["allocations"] = json.dumps(allocations)

        # Monthly payments
        if validated_data["payment_times"] == TYPE_MONTHLY:
            return self.monthly_payment(person, allocations)

        # Direct payments
        payment_type = DonsConfig.PAYMENT_TYPE
        if validated_data["to"] == TO_2022:
            payment_type = Presidentielle2022Config.DONATION_PAYMENT_TYPE

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
