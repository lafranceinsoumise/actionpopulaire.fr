from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import status
from rest_framework.generics import (
    GenericAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    get_object_or_404,
    CreateAPIView,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from agir.lib.rest_framework_permissions import (
    GlobalOrObjectPermissions,
    GlobalOnlyPermissions,
)
from agir.people.models import Person
from agir.people.serializers import (
    SubscriptionRequestSerializer,
    ManageNewslettersRequestSerializer,
    RetrievePersonRequestSerializer,
    PersonSerializer,
)
from agir.people.actions.subscription import SUBSCRIPTION_TYPE_AP


class SubscriptionAPIView(GenericAPIView):
    """
    Sign-up first step endpoint for external users (e.g. Wordpress)
    """

    serializer_class = SubscriptionRequestSerializer
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (GlobalOnlyPermissions,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.result_data, status=status.HTTP_201_CREATED)


class SignupAPIView(SubscriptionAPIView):
    """
    Sign-up first step endpoint for Action Populaire users
    """

    permission_classes = ()

    def post(self, request, *args, **kwargs):
        request.data.update({"type": SUBSCRIPTION_TYPE_AP})
        return super().post(request, *args, **kwargs)


class PersonProfilePermissions(GlobalOrObjectPermissions):
    perms_map = {"OPTIONS": [], "GET": [], "PUT": [], "PATCH": []}
    object_perms_map = {
        "OPTIONS": ["people.view_person"],
        "GET": ["people.view_person"],
        "PUT": ["people.change_person"],
        "PATCH": ["people.change_person"],
    }


class PersonProfileAPIView(RetrieveUpdateAPIView):
    serializer_class = PersonSerializer
    queryset = Person.objects.all()
    permission_classes = (PersonProfilePermissions,)

    def get_object(self):
        person = None
        if hasattr(self.request.user, "person"):
            person = self.request.user.person
        self.check_object_permissions(self.request, person)
        return person

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=[
                "id",
                "displayName",
                "firstName",
                "lastName",
                "zip",
                "contactPhone",
                "isInsoumise",
                "is2022",
                "mandat",
            ],
            **kwargs,
        )


class CounterAPIView(GenericAPIView):
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (GlobalOnlyPermissions,)

    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(cache_page(60))
    def get(self, request, *args, **kwargs):
        return Response(
            {"value": Person.objects.filter(is_2022=True).count()},
            status=status.HTTP_200_OK,
        )


class ManageNewslettersAPIView(GenericAPIView):
    serializer_class = ManageNewslettersRequestSerializer
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (GlobalOnlyPermissions,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "ok"}, status=status.HTTP_200_OK)


class RetrievePersonView(RetrieveAPIView):
    serializer_class = PersonSerializer
    queryset = Person.objects.all()  # pour les permissions
    permission_classes = (
        GlobalOrObjectPermissions,
    )  # attention si on rajoute de l'édition sur ce point

    def get_object(self):
        serializer = RetrievePersonRequestSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        obj = serializer.retrieve()
        self.check_object_permissions(self.request, obj)
        return obj


class ReferrerInformationView(APIView):
    # accessible à tous
    permission_classes = ()

    def get(self, request, *args, referrer_id, **kwargs):
        person = get_object_or_404(Person, referrer_id=referrer_id)
        nom = f"{person.first_name} {person.last_name}".strip()
        if not nom:
            raise Http404
        return Response(nom, status.HTTP_200_OK)
