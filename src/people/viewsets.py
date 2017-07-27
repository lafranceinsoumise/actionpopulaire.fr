from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import list_route
import django_filters

from lib.pagination import LegacyPaginator
from lib.permissions import RestrictViewPermissions
from lib.views import NationBuilderViewMixin
from authentication.models import Role

from . import serializers, models


class PeopleFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = models.Person
        fields = ['email', 'tags']


class LegacyPersonViewSet(NationBuilderViewMixin, ModelViewSet):
    """
    Legacy endpoint for people that imitates the endpoint from Eve Python
    """
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacyPersonSerializer
    queryset = models.Person.objects.all()
    permission_classes = (RestrictViewPermissions, )
    filter_class = PeopleFilter

    @list_route()
    def me(self, request):
        self.kwargs['pk'] = self.request.user.person.pk
        return self.retrieve(request)

    def get_queryset(self):
        if not self.request.user.has_perm('people.view_person'):
            if hasattr(self.request.user, 'type') and self.request.user.type == Role.PERSON_ROLE:
                return self.queryset.filter(pk=self.request.user.person.pk)
            else:
                return self.queryset.none()
        return super(LegacyPersonViewSet, self).get_queryset()


class PersonTagViewSet(ModelViewSet):
    """
    Endpoint for person tags
    """
    serializer_class = serializers.PersonTagSerializer
    queryset = models.PersonTag.objects.all()
    permission_classes = (RestrictViewPermissions, )
