from rest_framework import permissions
from rest_framework.generics import CreateAPIView

from agir.donations.serializers import CreateDonationSerializer, SendDonationSerializer
from agir.people.models import Person


class CreateDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CreateDonationSerializer
    queryset = Person.objects.none()


class SendDonationAPIView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SendDonationSerializer
    queryset = Person.objects.none()
