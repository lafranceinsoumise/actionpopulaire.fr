from django.db.models import Q
import django_filters
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.decorators import list_route

from lib.permissions import PermissionsOrReadOnly, RestrictViewPermissions, DjangoModelPermissions
from lib.pagination import LegacyPaginator
from lib.filters import LegacyDistanceFilter
from lib.views import NationBuilderViewMixin, CreationSerializerMixin

from authentication.models import Role

from . import serializers, models


class SupportGroupFilterSet(django_filters.rest_framework.FilterSet):
    closeTo = LegacyDistanceFilter(name='coordinates', lookup_expr='distance_lte')
    path = django_filters.CharFilter(name='nb_path', lookup_expr='exact')

    class Meta:
        model = models.SupportGroup
        fields = ('contact_email', 'closeTo', 'path',)


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

        serializer = serializers.GroupMembershipBulkSerializer(memberships, data=request.data, many=True,
                                                               context=context)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)
