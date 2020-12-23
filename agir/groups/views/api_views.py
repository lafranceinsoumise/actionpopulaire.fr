from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from agir.groups.filters import GroupAPIFilterSet
from agir.groups.models import SupportGroup, SupportGroupSubtype
from agir.groups.serializers import (
    SupportGroupLegacySerializer,
    SupportGroupSubtypeSerializer,
)
from agir.lib.pagination import APIPaginator

__all__ = ["GroupSearchAPIView", "GroupSubtypesView"]


class GroupSearchAPIView(ListAPIView):
    queryset = SupportGroup.objects.active()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupAPIFilterSet
    serializer_class = SupportGroupLegacySerializer
    pagination_class = APIPaginator
    permission_classes = (IsAuthenticated,)


class GroupSubtypesView(ListAPIView):
    serializer_class = SupportGroupSubtypeSerializer
    queryset = SupportGroupSubtype.objects.filter(
        visibility=SupportGroupSubtype.VISIBILITY_ALL
    )
