from django.contrib.gis.db.models.functions import Distance
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from agir.groups.filters import GroupAPIFilterSet
from agir.groups.models import SupportGroup, SupportGroupSubtype
from agir.groups.serializers import (
    SupportGroupLegacySerializer,
    SupportGroupSubtypeSerializer,
    SupportGroupSerializer,
    SupportGroupDetailSerializer,
)
from agir.lib.pagination import APIPaginator

__all__ = [
    "GroupSearchAPIView",
    "GroupSubtypesView",
    "UserGroupsView",
    "GroupDetailAPIView",
]


class GroupSearchAPIView(ListAPIView):
    "Vieille API encore utilisée par le composant js groupSelector du formulaire de dons"

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


class UserGroupsView(ListAPIView):
    serializer_class = SupportGroupSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        person = self.request.user.person
        person_groups = (
            SupportGroup.objects.filter(memberships__person=self.request.user.person)
            .active()
            .annotate(membership_type=F("memberships__membership_type"))
            .order_by("-membership_type", "name")
        )
        if person_groups.count() == 0 and person.coordinates is not None:
            person_groups = SupportGroup.objects.active()
            if person.is_2022_only:
                person_groups = person_groups.is_2022()
            person_groups = person_groups.annotate(
                distance=Distance("coordinates", person.coordinates)
            ).order_by("distance")[:3]
            for group in person_groups:
                group.membership = None

        return person_groups


class GroupDetailAPIView(RetrieveAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = SupportGroupDetailSerializer
    queryset = SupportGroup.objects.all()
