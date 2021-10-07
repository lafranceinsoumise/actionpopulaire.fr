from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from agir.donations.serializers import CreateDonationSerializer, SendDonationSerializer
from agir.people.models import Person
from agir.groups.models import SupportGroup
from django.db import transaction
from agir.donations.views.donations_views import DONATION_SESSION_NAMESPACE
from agir.payments.actions.payments import (
    redirect_to_payment,
    create_payment,
)


class CreateDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CreateDonationSerializer
    queryset = Person.objects.none()


class SendDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SendDonationSerializer
    queryset = Person.objects.none()

    def update_person(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user_exist = False

        # Check user connected
        if request.user.is_authenticated and request.user.person is not None:
            if validated_data["email"] == request.user.person.email:
                user_exist = True

        # User exist : update user informations
        if user_exist:
            person = Person.objects.get(pk=request.user.person.id)
            # Update subscribed_lfi only if its true
            if not validated_data["subscribed_lfi"]:
                del validated_data["subscribed_lfi"]
            del validated_data["email"]

            print("validated_data to update", validated_data, flush=True)
            self.update_person(person, validated_data)
            # TODO: update phone, subscribed_lfi

            # Update from filter
            # del validated_data["nationality"]
            # person = Person.objects.filter(pk=request.user.person.id)
            # person.update(**validated_data)

        # Add anonymous person in payment
        else:
            person = Person.objects.create(**validated_data)

        # Get donations info from session
        session_donation = request.session[DONATION_SESSION_NAMESPACE]
        amount = session_donation["amount"]
        type = session_donation["type"]
        to = session_donation["to"]
        allocations = session_donation["allocations"]
        # No group donation by default
        amount_group = 0

        # 2 payments (group + national)
        if to == "LFI":
            if allocations:
                group_id = allocations["group"]
                amount_group = allocations["amount"]
                # Check group exist and certified
                group = SupportGroup.objects.get(pk=group_id, is_certified=True)
                # amount national = amount - amount_group
                # amount = amount - amount_group

        with transaction.atomic():
            # TODO : payments only if amount > 0 or amount_group > 0:
            payment = create_payment(
                person=person, type=type, price=amount, meta=validated_data, **kwargs,
            )

        self.clear_session()
        return redirect_to_payment(payment)
