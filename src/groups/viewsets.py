import django_filters
from rest_framework.viewsets import ModelViewSet

from lib.permissions import PermissionsOrReadOnly
from lib.pagination import LegacyPaginator
from lib.filters import LegacyDistanceFilter
from lib.views import NationBuilderViewMixin

from . import serializers, models


class SupportGroupFilterSet(django_filters.rest_framework.FilterSet):
    closeTo = LegacyDistanceFilter(name='coordinates', lookup_expr='distance_lte')
    path = django_filters.CharFilter(name='nb_path', lookup_expr='exact')

    class Meta:
        model = models.SupportGroup
        fields = ('contact_email', 'closeTo', 'path', )


class LegacySupportGroupViewSet(NationBuilderViewMixin, ModelViewSet):
    """
    Legacy endpoint for events that imitates the endpoint from Eve Python
    """
    permission_classes = (PermissionsOrReadOnly,)
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacySupportGroupSerializer
    queryset = models.SupportGroup.objects.all().prefetch_related('tags')
    filter_class = SupportGroupFilterSet


class SupportGroupTagViewSet(ModelViewSet):
    """
    EventTag viewset
    """
    serializer_class = serializers.SupportGroupTagSerializer
    queryset = models.SupportGroupTag.objects.all()


class MembershipViewSet(ModelViewSet):
    """

    """

    serializer_class = serializers.MembershipSerializer
    queryset = models.Membership.objects.select_related('support_group', 'person')
