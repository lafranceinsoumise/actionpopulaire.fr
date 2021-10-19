from django.http.response import JsonResponse
from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from agir.donations.serializers import CreateDonationSerializer, SendDonationSerializer
from agir.people.models import Person, PersonEmail
from django.db import transaction
from agir.donations.views.donations_views import DONATION_SESSION_NAMESPACE
from agir.payments.actions.payments import create_payment
import json


class CreateDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CreateDonationSerializer
    queryset = Person.objects.none()


class SendDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SendDonationSerializer
    queryset = Person.objects.none()

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
            setattr(instance, attr, value)
        instance.save()
        return instance

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        email = validated_data["email"]
        amount = validated_data["amount"]
        type = validated_data["type"]

        connected_user = False
        person = None

        # Check user connected
        if request.user.is_authenticated and request.user.person is not None:
            if validated_data["email"] == request.user.person.email:
                connected_user = True
                del validated_data["email"]

        # User exist : update user informations
        if connected_user:
            person = Person.objects.get(pk=request.user.person.id)
            # Update subscribed_lfi only if its true
            if not validated_data["subscribed_lfi"]:
                del validated_data["subscribed_lfi"]

            self.update_person(person, validated_data)
        # Add anonymous person in payment
        else:
            # Check email exist
            if not PersonEmail.objects.filter(address__iexact=email).exists():
                person = self.create_person(validated_data)

        if "allocations" in validated_data:
            validated_data["allocations"] = json.dumps(
                [
                    {**allocation, "group": str(allocation["group"].id)}
                    for allocation in validated_data.get("allocations", [])
                ]
            )

        with transaction.atomic():
            payment = create_payment(
                person=person, type=type, price=amount, meta=validated_data, **kwargs,
            )

        return JsonResponse({"next": payment.get_payment_url()})
