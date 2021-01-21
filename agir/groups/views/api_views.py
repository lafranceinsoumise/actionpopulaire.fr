from django.contrib.gis.db.models.functions import Distance
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.groups.filters import GroupAPIFilterSet
from agir.groups.models import SupportGroup, SupportGroupSubtype
from agir.groups.serializers import (
    SupportGroupLegacySerializer,
    SupportGroupSubtypeSerializer,
    SupportGroupSerializer,
    SupportGroupDetailSerializer,
)
from agir.events.models import Event
from agir.events.serializers import EventSerializer
from agir.lib.pagination import APIPaginator

__all__ = [
    "GroupSearchAPIView",
    "GroupSubtypesView",
    "UserGroupsView",
    "GroupDetailAPIView",
    "NearGroupsAPIView",
    "GroupEventsAPIView",
    "GroupPastEventsAPIView",
    "GroupUpcomingEventsAPIView",
    "GroupPastEventReportsAPIView",
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
    queryset = SupportGroup.objects.active()


class NearGroupsAPIView(ListAPIView):
    serializer_class = SupportGroupDetailSerializer
    queryset = SupportGroup.objects.active()

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=["id", "name", "iconConfiguration", "location",], **kwargs
        )

    def get_queryset(self):
        if self.supportgroup.coordinates is None:
            return SupportGroup.objects.none()

        groups = (
            SupportGroup.objects.active()
            .exclude(pk=self.supportgroup.pk)
            .exclude(coordinates__isnull=True)
        )

        if self.supportgroup.is_2022:
            groups = groups.is_2022()

        groups = groups.annotate(
            distance=Distance("coordinates", self.supportgroup.coordinates)
        ).order_by("distance")

        return groups[:3]

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.active().get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupEventsAPIView(ListAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = EventSerializer
    queryset = Event.objects.listed()

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .distinct()
            .order_by("-start_time")
        )
        return events

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupUpcomingEventsAPIView(ListAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = EventSerializer
    queryset = Event.objects.listed().upcoming()

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .upcoming()
            .distinct()
            .order_by("start_time")
        )
        return events

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupPastEventsAPIView(ListAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = EventSerializer
    queryset = Event.objects.listed().past()
    pagination_class = APIPaginator

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .past()
            .distinct()
            .order_by("-start_time")
        )
        return events

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)


class GroupPastEventReportsAPIView(ListAPIView):
    permission_ = ("groups.view_supportgroup",)
    serializer_class = EventSerializer
    queryset = Event.objects.listed().past()

    def get_queryset(self):
        events = (
            self.supportgroup.organized_events.listed()
            .past()
            .exclude(report_content="")
            .distinct()
            .order_by("-start_time")
        )
        return events

    def dispatch(self, request, pk, *args, **kwargs):
        try:
            self.supportgroup = SupportGroup.objects.get(pk=pk)
        except SupportGroup.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return super().dispatch(request, *args, **kwargs)
