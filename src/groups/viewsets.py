import django_filters
from django_filters.rest_framework.backends import DjangoFilterBackend
from django.views.decorators.cache import cache_control
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import list_route, authentication_classes

from lib.permissions import PermissionsOrReadOnly, RestrictViewPermissions, DjangoModelPermissions
from lib.pagination import LegacyPaginator
from lib.filters import DistanceFilter, OrderByDistanceToBackend
from lib.views import NationBuilderViewMixin, CreationSerializerMixin

from authentication.models import Role

from . import serializers, models


class SupportGroupFilterSet(django_filters.rest_framework.FilterSet):
    close_to = DistanceFilter(name='coordinates', lookup_expr='distance_lte')
    path = django_filters.CharFilter(name='nb_path', lookup_expr='exact')

    class Meta:
        model = models.SupportGroup
        fields = ('contact_email', 'close_to', 'path',)


class LegacySupportGroupViewSet(NationBuilderViewMixin, ModelViewSet):
    """
    Legacy endpoint for events that imitates the endpoint from Eve Python
    """
    permission_classes = (PermissionsOrReadOnly,)
    pagination_class = LegacyPaginator
    serializer_class = serializers.LegacySupportGroupSerializer
    queryset = models.SupportGroup.objects.all().prefetch_related('tags')
    filter_backends = (DjangoFilterBackend, OrderByDistanceToBackend)
    filter_class = SupportGroupFilterSet

    def get_queryset(self):
        if not self.request.user.has_perm('groups.view_hidden_supportgroup'):
            return self.queryset.filter(published=True)
        return super(LegacySupportGroupViewSet, self).get_queryset()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        group = models.SupportGroup.objects.get(pk=response.data['_id'])
        membership = models.Membership.objects.create(
            person=request.user.person,
            supportgroup=group,
            is_manager=True,
            is_referent=True,
        )

        return response

    @list_route(methods=['GET'])
    @cache_control(max_age=60, public=True)
    @authentication_classes([])
    def summary(self, request, *args, **kwargs):
        supportgroups = self.get_queryset().all()
        serializer = serializers.SummaryGroupSerializer(
            instance=supportgroups,
            many=True,
            context=self.get_serializer_context()
        )
        return Response(data=serializer.data)


class SupportGroupTagViewSet(ModelViewSet):
    """
    EventTag viewset
    """
    serializer_class = serializers.SupportGroupTagSerializer
    queryset = models.SupportGroupTag.objects.all()
    permission_classes = (PermissionsOrReadOnly,)


class MembershipViewSet(ModelViewSet):
    """

    """

    serializer_class = serializers.MembershipSerializer
    queryset = models.Membership.objects.select_related('supportgroup', 'person')
    creation_serializer_class = serializers.MembershipCreationSerializer
    permission_classes = (RestrictViewPermissions,)

    def get_queryset(self):
        queryset = super(MembershipViewSet, self).get_queryset()

        if not self.request.user.has_perm('groups.view_membership'):
            if hasattr(self.request.user, 'type') and self.request.user.type == Role.PERSON_ROLE:
                return queryset.filter(person=self.request.user.person)
            else:
                return queryset.none()
        return queryset


class NestedMembershipViewSet(CreationSerializerMixin, NestedViewSetMixin, ModelViewSet):
    """

    """
    serializer_class = serializers.MembershipSerializer
    queryset = models.Membership.objects.select_related('supportgroup', 'person')
    permission_classes = (RestrictViewPermissions,)
    creation_serializer_class = serializers.GroupMembershipCreatableSerializer

    def get_queryset(self):
        queryset = super(NestedMembershipViewSet, self).get_queryset()

        if not self.request.user.has_perm('groups.view_membership'):
            if hasattr(self.request.user, 'type') and self.request.user.type == Role.PERSON_ROLE:
                if queryset.filter(person=self.request.user.person, is_manager=True).exists():
                    return queryset
                return queryset.filter(person=self.request.user.person)
            else:
                return queryset.none()
        return queryset

    def get_serializer_context(self):
        parents_query_dict = self.get_parents_query_dict()
        context = super(NestedMembershipViewSet, self).get_serializer_context()
        context.update(parents_query_dict)
        return context

    @list_route(methods=['PUT'], permission_classes=(DjangoModelPermissions,))
    def bulk(self, request, *args, **kwargs):
        parents_query_dict = self.get_parents_query_dict()
        memberships = models.Membership.objects.filter(**parents_query_dict)

        context = self.get_serializer_context()
        context.update(parents_query_dict)

        serializer = serializers.GroupMembershipBulkSerializer(
            memberships,
            data=request.data,
            many=True,
            context=context)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)


class SupportGroupSubtypeViewSet(ModelViewSet):
    permission_classes = (PermissionsOrReadOnly,)
    serializer_class = serializers.SupportGroupSubtypeSerializer
    queryset = models.SupportGroupSubtype.objects.exclude(privileged_only=True)