from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.response import Response

from agir.lib.rest_framework_permissions import RestrictViewPermissions
from agir.people.models import Person
from agir.people.serializers import (
    SubscriptionRequestSerializer,
    ManageNewslettersRequestSerializer,
    RetrievePersonRequestSerializer,
    PersonSerializer,
)


class SubscriptionAPIView(GenericAPIView):
    serializer_class = SubscriptionRequestSerializer
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (RestrictViewPermissions,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.result_data, status=status.HTTP_201_CREATED)


class CounterAPIView(GenericAPIView):
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (RestrictViewPermissions,)

    def get(self, request, *args, **kwargs):
        return Response(
            {"value": Person.objects.filter(is_2022=True).count()},
            status=status.HTTP_200_OK,
        )


class ManageNewslettersAPIView(GenericAPIView):
    serializer_class = ManageNewslettersRequestSerializer
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (RestrictViewPermissions,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class RetrievePersonView(RetrieveAPIView):
    serializer_class = PersonSerializer
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (RestrictViewPermissions,)

    def get_object(self):
        serializer = RetrievePersonRequestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return serializer.retrieve()
