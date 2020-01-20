from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from agir.groups.filters import GroupAPIFilterSet
from agir.groups.models import SupportGroup, SupportGroupSubtype
from agir.groups.serializers import (
    SupportGroupSerializer,
    SupportGroupSubtypeSerializer,
)
from agir.lib.pagination import APIPaginator

__all__ = ["GroupSearchAPIView", "GroupSubtypesView"]


class GroupSearchAPIView(ListAPIView):
    queryset = SupportGroup.objects.active()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupAPIFilterSet
    serializer_class = SupportGroupSerializer
    pagination_class = APIPaginator


class GroupSubtypesView(ListAPIView):
    serializer_class = SupportGroupSubtypeSerializer
    queryset = SupportGroupSubtype.objects.filter(
        visibility=SupportGroupSubtype.VISIBILITY_ALL
    )
