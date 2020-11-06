from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
import django_filters

from agir.lib.pagination import LegacyPaginator
from agir.lib.rest_framework_permissions import RestrictViewPermissions
from agir.lib.views import NationBuilderViewMixin
from agir.authentication.models import Role
from agir.people.models import PersonEmail, PersonEmailManager
from agir.people.token_buckets import SubscribeIPBucket, SubscribeEmailBucket

from . import serializers, models


class PeopleFilter(django_filters.rest_framework.FilterSet):
    email = django_filters.CharFilter(
        field_name="emails__address", lookup_expr="iexact"
    )

    class Meta:
        model = models.Person
        fields = ["tags"]


class LegacyPersonViewSet(NationBuilderViewMixin, ModelViewSet):
    """
    Legacy endpoint for people that imitates the endpoint from Eve Python
    """

    pagination_class = LegacyPaginator
    queryset = models.Person.objects.all()
    permission_classes = (RestrictViewPermissions,)
    filterset_class = PeopleFilter

    @action(detail=False)
    def me(self, request):
        self.kwargs["pk"] = self.request.user.person.pk
        return self.retrieve(request)

    @action(methods=["POST"], detail=False)
    def subscribe(self, request, *args, **kwargs):
        ip = request.META.get("HTTP_X_WORDPRESS_CLIENT")
        if not ip or not SubscribeIPBucket.has_tokens(ip):
            raise PermissionDenied()

        serializer = serializers.SubscriptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not SubscribeEmailBucket.has_tokens(
            PersonEmailManager.normalize_email(serializer.validated_data["email"])
        ):
            raise PermissionDenied()

        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def get_queryset(self):
        if not (
            "pk" in self.kwargs or self.request.user.has_perm("people.view_person")
        ):
            if (
                hasattr(self.request.user, "type")
                and self.request.user.type == Role.PERSON_ROLE
            ):
                return self.queryset.filter(pk=self.request.user.person.pk)
            else:
                return self.queryset.none()
        return super(LegacyPersonViewSet, self).get_queryset()

    def get_serializer_class(self):
        if not self.request.user.has_perm("people.view_person"):
            return serializers.LegacyUnprivilegedPersonSerializer
        return serializers.LegacyPersonSerializer


class PersonTagViewSet(ModelViewSet):
    """
    Endpoint for person tags
    """

    serializer_class = serializers.PersonTagSerializer
    queryset = models.PersonTag.objects.all()
    permission_classes = (RestrictViewPermissions,)
