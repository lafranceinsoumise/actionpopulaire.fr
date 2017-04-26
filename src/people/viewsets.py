from rest_framework.viewsets import ModelViewSet

from lib.pagination import LegacyPaginator
from lib.permissions import RestrictViewPermissions

from . import serializers, models


class LegacyPersonViewSet(ModelViewSet):
    """
    Legacy endpoint for people that imitates the endpoint from Eve Python
    """
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacyPersonSerializer
    queryset = models.Person.objects.all()
    permission_classes = (RestrictViewPermissions, )

    def get_queryset(self):
        if not self.request.user.has_perm('people.view_person'):
            return self.queryset.filter(pk=self.request.user.pk)
        return super(LegacyPersonViewSet, self).get_queryset()


class PersonTagViewSet(ModelViewSet):
    """
    Endpoint for person tags
    """
    serializer_class = serializers.PersonTagSerializer
    queryset = models.PersonTag.objects.all()
    permission_classes = (RestrictViewPermissions, )
