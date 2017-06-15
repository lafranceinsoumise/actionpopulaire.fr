from django.utils import timezone
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import list_route
from rest_framework.response import Response
from authentication.models import Role
import django_filters

from lib.permissions import PermissionsOrReadOnly, RestrictViewPermissions, DjangoModelPermissions
from lib.pagination import LegacyPaginator
from lib.filters import LegacyDistanceFilter
from lib.views import NationBuilderViewMixin, CreationSerializerMixin

from . import serializers, models


class EventFilterSet(django_filters.rest_framework.FilterSet):
    closeTo = LegacyDistanceFilter(name='coordinates', lookup_expr='distance_lte')
    after = django_filters.DateTimeFilter(name='start_time', lookup_expr='gte')
    before = django_filters.DateTimeFilter(name='start_time', lookup_expr='lte')
    path = django_filters.CharFilter(name='nb_path', lookup_expr='exact')

    class Meta:
        model = models.Event
        fields = ('contact_email', 'start_time', 'closeTo', 'path', )


class LegacyEventViewSet(NationBuilderViewMixin, ModelViewSet):
    """
    Legacy endpoint for events that imitates the endpoint from Eve Python
    """
    permission_classes = (PermissionsOrReadOnly,)
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacyEventSerializer
    queryset = models.Event.objects.filter(end_time__date__gte=timezone.now()) \
        .select_related('calendar').prefetch_related('tags')
    filter_class = EventFilterSet


class CalendarViewSet(ModelViewSet):
    """
    Calendar Viewset !
    """
    serializer_class = serializers.CalendarSerializer
    queryset = models.Calendar.objects.all()


class EventTagViewSet(ModelViewSet):
    """
    EventTag viewset
    """
    serializer_class = serializers.EventTagSerializer
    queryset = models.EventTag.objects.all()


class RSVPViewSet(CreationSerializerMixin, ModelViewSet):
    """

    """
    def get_queryset(self):
        queryset = super(RSVPViewSet, self).get_queryset()

        if not self.request.user.has_perm('events.view_rsvp'):
            if hasattr(self.request.user, 'type') and self.request.user.type == Role.PERSON_ROLE:
                return queryset.filter(person=self.request.user.person)
            else:
                return queryset.none()
        return queryset

    serializer_class = serializers.RSVPSerializer
    creation_serializer_class = serializers.RSVPCreationSerializer
    queryset = models.RSVP.objects.select_related('event', 'person')
    permission_classes = (RestrictViewPermissions, )


class NestedRSVPViewSet(CreationSerializerMixin, NestedViewSetMixin, ModelViewSet):
    """

    """
    serializer_class = serializers.RSVPSerializer
    queryset = models.RSVP.objects.select_related('event', 'person')
    permission_classes = (RestrictViewPermissions,)
    creation_serializer_class = serializers.EventRSVPCreatableSerializer

    def get_queryset(self):
        queryset = super(NestedRSVPViewSet, self).get_queryset()

        if not self.request.user.has_perm('events.view_rsvp'):
            if hasattr(self.request.user, 'type') and self.request.user.type == Role.PERSON_ROLE:
                return queryset.filter(Q(person=self.request.user.person) | Q(event__organizers=self.request.user.person))
            else:
                return queryset.none()
        return queryset

    def get_serializer_context(self):
        parents_query_dict = self.get_parents_query_dict()
        context = super(NestedRSVPViewSet, self).get_serializer_context()
        context.update(parents_query_dict)
        return context

    @list_route(methods=['PUT'], permission_classes=(DjangoModelPermissions,))
    def bulk(self, request, *args, **kwargs):
        parents_query_dict = self.get_parents_query_dict()
        rsvps = models.RSVP.objects.filter(**parents_query_dict)

        context = self.get_serializer_context()
        context.update(parents_query_dict)

        serializer = serializers.EventRSVPBulkSerializer(rsvps, data=request.data, many=True, context=context)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)
