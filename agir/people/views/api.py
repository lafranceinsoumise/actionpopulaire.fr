from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response

from agir.people.models import Person
from agir.people.serializers import SubscriptionRequestSerializer


class SubscriptionAPIView(GenericAPIView):
    serializer_class = SubscriptionRequestSerializer
    queryset = Person.objects.all()  # pour les permissions

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.result_data, status=status.HTTP_201_CREATED)


class CounterAPIView(GenericAPIView):
    queryset = Person.objects.all()  # pour les permissions

    def get(self, request, *args, **kwargs):
        return Response(
            {"value": Person.objects.filter(is_2022=True).count()},
            status=status.HTTP_200_OK,
        )
