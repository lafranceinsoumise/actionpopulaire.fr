from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView

from agir.groups.filters import GroupAPIFilterSet
from agir.groups.models import SupportGroup
from agir.groups.serializers import SupportGroupSerializer
from agir.lib.pagination import APIPaginator

__all__ = ["GroupSearchAPIView"]


class GroupSearchAPIView(ListAPIView):
    queryset = SupportGroup.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupAPIFilterSet
    serializer_class = SupportGroupSerializer
    pagination_class = APIPaginator
