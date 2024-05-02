import datetime
import re

import reversion
from dateutil.relativedelta import relativedelta
from django.contrib.gis.db.models.functions import Distance
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import (
    Max,
    DateTimeField,
    Q,
    F,
    Sum,
    Count,
    Value,
    CharField,
    Avg,
    ExpressionWrapper,
    DurationField,
)
from django.db.models.functions import Greatest, Concat
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, exceptions
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

from agir.donations.allocations import get_supportgroup_balance
from agir.donations.models import SpendingRequest
from agir.events.models import Event, RSVP, EventSubtype
from agir.events.serializers import EventListSerializer, DisplayEventSubtypeSerializer
from agir.groups.actions.notifications import (
    new_message_notifications,
    new_comment_notifications,
    someone_joined_notification,
)
from agir.groups.filters import GroupAPIFilterSet, GroupLocationAPIFilterSet
from agir.groups.models import (
    SupportGroup,
    SupportGroupSubtype,
    Membership,
    SupportGroupExternalLink,
)
from agir.groups.proxys import ThematicGroup
from agir.groups.serializers import (
    SupportGroupLegacySerializer,
    SupportGroupSubtypeSerializer,
    SupportGroupSerializer,
    SupportGroupDetailSerializer,
    SupportGroupUpdateSerializer,
    MembershipSerializer,
    SupportGroupExternalLinkSerializer,
    MemberPersonalInformationSerializer,
    ThematicGroupSerializer,
)
from agir.groups.utils.supportgroup import is_active_group_filter
from agir.lib.pagination import (
    APIPageNumberPagination,
)
from agir.msgs.actions import update_recipient_message
from agir.msgs.serializers import SupportGroupMessageParticipantSerializer
from agir.people.models import Person

__all__ = [
    "LegacyGroupSearchAPIView",
    "GroupSearchAPIView",
    "GroupLocationSearchAPIView",
    "GroupSubtypesView",
    "UserGroupsView",
    "ThematicGroupsView",
    "UserGroupSuggestionsView",
    "GroupDetailAPIView",
    "NearGroupsAPIView",
    "GroupEventsAPIView",
    "GroupPastEventsAPIView",
    "GroupUpcomingEventsAPIView",
    "GroupPastEventReportsAPIView",
    "GroupEventsJoinedAPIView",
    "GroupMessagesAPIView",
    "GroupMessageNotificationStatusAPIView",
    "GroupMessageLockedStatusAPIView",
    "GroupMessagesPrivateAPIView",
    "GroupSingleMessageAPIView",
    "GroupMessageCommentsAPIView",
    "GroupSingleCommentAPIView",
    "GroupMessageParticipantsAPIView",
    "JoinGroupAPIView",
    "FollowGroupAPIView",
    "QuitGroupAPIView",
    "GroupMembersAPIView",
    "GroupUpdateAPIView",
    "GroupInvitationAPIView",
    "MemberPersonalInformationAPIView",
    "GroupMemberUpdateAPIView",
    "GroupFinanceAPIView",
    "CreateSupportGroupExternalLinkAPIView",
    "RetrieveUpdateDestroySupportGroupExternalLinkAPIView",
    "GroupUpdateOwnMembershipAPIView",
    "GroupStatisticsAPIView",
]

from agir.lib.rest_framework_permissions import (
    GlobalOrObjectPermissions,
    IsPersonPermission,
    IsActionPopulaireClientPermission,
    IsPersonOrTokenHasScopePermission,
)
from agir.msgs.models import (
    SupportGroupMessage,
    SupportGroupMessageComment,
    SupportGroupMessageRecipient,
)

from agir.msgs.serializers import (
    SupportGroupMessageSerializer,
    MessageCommentSerializer,
)

from agir.groups.tasks import invite_to_group


class LegacyGroupSearchAPIView(ListAPIView):
    "Vieille API encore utilisée par le composant js groupSelector du formulaire de dons"

    queryset = SupportGroup.objects.active().prefetch_related("subtypes")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupAPIFilterSet
    serializer_class = SupportGroupLegacySerializer
    pagination_class = APIPageNumberPagination
    permission_classes = (IsPersonPermission,)


class GroupSearchAPIView(ListAPIView):
    queryset = SupportGroup.objects.active()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupAPIFilterSet
    serializer_class = SupportGroupDetailSerializer
    pagination_class = APIPageNumberPagination
    permission_classes = (IsActionPopulaireClientPermission,)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=[
                "id",
                "name",
                "type",
                "location",
                "commune",
            ],
            **kwargs,
        )


class GroupLocationSearchAPIView(ListAPIView):
    queryset = SupportGroup.objects.active()
    permission_classes = (IsActionPopulaireClientPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = GroupLocationAPIFilterSet

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            data = (
                page.annotate(zip=F("location_zip"))
                .order_by("zip", "name")
                .values("id", "name", "zip")
            )
            return self.get_paginated_response(data)

        data = (
            queryset.annotate(zip=F("location_zip"))
            .order_by("zip", "name")
            .values("id", "name", "zip")
        )
        return Response(data)


class GroupSubtypesView(ListAPIView):
    serializer_class = SupportGroupSubtypeSerializer
    queryset = SupportGroupSubtype.objects.filter(
        visibility=SupportGroupSubtype.VISIBILITY_ALL
    )


class UserGroupsView(ListAPIView):
    serializer_class = SupportGroupSerializer
    permission_classes = (IsPersonOrTokenHasScopePermission,)
    required_scopes = ("view_membership",)
    queryset = SupportGroup.objects.active()

    def get_queryset(self):
        return (
            SupportGroup.objects.active()
            .with_serializer_prefetch(person=self.request.user.person)
            .filter(
                id__in=self.request.user.person.supportgroups.values_list(
                    "id", flat=True
                )
            )
            .order_by("name")
        )


class UserGroupSuggestionsView(ListAPIView):
    serializer_class = SupportGroupSerializer
    permission_classes = (IsPersonPermission,)
    queryset = SupportGroup.objects.active()

    def get_queryset(self):
        person = self.request.user.person

        if person.coordinates is None:
            return self.queryset.none()

        base_queryset = (
            self.queryset.filter(is_active_group_filter())
            .exclude(pk__in=person.supportgroups.values_list("id", flat=True))
            .with_serializer_prefetch()
        )

        # Try to find groups in person action radius first
        near_groups = base_queryset.near(
            coordinates=person.coordinates, radius=person.action_radius
        ).order_by("distance")[:3]

        if len(near_groups) > 0:
            return near_groups

        # Fallback on all groups
        return base_queryset.annotate(
            distance=Distance("coordinates", person.coordinates)
        ).order_by("distance")[:3]


class GroupDetailPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": []}
    object_perms_map = {
        "GET": ["groups.view_supportgroup"],
    }


class ThematicGroupsView(ListAPIView):
    serializer_class = ThematicGroupSerializer
    permission_classes = (
        IsActionPopulaireClientPermission,
        GroupDetailPermissions,
    )
    queryset = (
        ThematicGroup.objects.visible()
        .prefetch_related("subtypes", "links")
        .order_by("name")
    )


class GroupDetailAPIView(RetrieveAPIView):
    permission_classes = (
        IsActionPopulaireClientPermission,
        GroupDetailPermissions,
    )
    serializer_class = SupportGroupDetailSerializer
    queryset = SupportGroup.objects.active()

    def get_serializer(self, *args, **kwargs):
        is_manager = (
            hasattr(self.request.user, "person")
            and self.request.user.person in self.get_object().managers
        )
        if not is_manager:
            return super().get_serializer(
                *args, fields=SupportGroupDetailSerializer.NON_MANAGER_FIELDS, **kwargs
            )
        return super().get_serializer(*args, **kwargs)


class NearGroupsAPIView(ListAPIView):
    permission_classes = (
        IsActionPopulaireClientPermission,
        GroupDetailPermissions,
    )
    serializer_class = SupportGroupDetailSerializer
    queryset = SupportGroup.objects.active()

    def initial(self, request, *args, **kwargs):
        self.supportgroup = get_object_or_404(
            SupportGroup.objects.active(), pk=kwargs.get("pk")
        )
        self.check_object_permissions(request, self.supportgroup)
        super().initial(request, *args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=["id", "name", "iconConfiguration", "location", "routes"],
            **kwargs,
        )

    def get_queryset(self):
        if self.supportgroup.coordinates is None:
            return SupportGroup.objects.none()

        groups = (
            (
                SupportGroup.objects.active()
                .exclude(pk=self.supportgroup.pk)
                .filter(coordinates__isnull=False, coordinates_type__isnull=False)
            )
            .annotate(distance=Distance("coordinates", self.supportgroup.coordinates))
            .order_by("distance")
        )

        return groups[:3]


class GroupEventListAPIView(ListAPIView):
    permission_classes = (
        IsActionPopulaireClientPermission,
        GroupDetailPermissions,
    )
    serializer_class = EventListSerializer
    queryset = Event.objects.all()
    order_by = "start_time"

    def check_permissions(self, request):
        self.person = None
        if self.request.user.is_authenticated and hasattr(self.request.user, "person"):
            self.person = self.request.user.person
        self.supportgroup = get_object_or_404(
            SupportGroup.objects.active(), pk=self.kwargs.get("pk")
        )
        super().check_permissions(request)
        self.check_object_permissions(request, self.supportgroup)

    def get_event_queryset(self):
        return self.queryset.filter(
            Q(organizers_groups__in=(self.supportgroup,))
            | Q(groups_attendees__in=(self.supportgroup,))
        )

    def get_queryset(self):
        return (
            self.get_event_queryset()
            .with_serializer_prefetch(self.person)
            .listed()
            .distinct(re.sub(r"^-", "", self.order_by), "pk")
            .order_by(self.order_by, "pk")
        )

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args,
            fields=EventListSerializer.EVENT_CARD_FIELDS,
            **kwargs,
        )


class GroupEventsAPIView(GroupEventListAPIView):
    def get_event_queryset(self):
        return self.supportgroup.organized_events.all()


class GroupEventsJoinedAPIView(GroupEventListAPIView):
    def get_event_queryset(self):
        return self.supportgroup.attended_event.all()


class GroupUpcomingEventsAPIView(GroupEventListAPIView):
    def get_event_queryset(self):
        return super().get_event_queryset().upcoming()


class GroupPastEventsAPIView(GroupEventListAPIView):
    pagination_class = APIPageNumberPagination
    order_by = "-start_time"

    def get_event_queryset(self):
        return super().get_event_queryset().past()


class GroupPastEventReportsAPIView(GroupEventListAPIView):
    order_by = "-start_time"

    def get_event_queryset(self):
        return self.supportgroup.organized_events.past().exclude(report_content="")


class GroupMessagesPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "POST": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessages"],
        "POST": ["msgs.add_supportgroupmessage"],
    }


class GroupMessagePermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "POST": [], "PATCH": [], "PUT": [], "DELETE": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "POST": ["msgs.add_supportgroupmessage"],
        "PATCH": ["msgs.change_supportgroupmessage"],
        "PUT": ["msgs.change_supportgroupmessage"],
        "DELETE": ["msgs.delete_supportgroupmessage"],
    }


class GroupMessagesNotificationPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "PUT": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "PUT": ["msgs.view_supportgroupmessage"],
    }


class GroupMessagesLockPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "PUT": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "PUT": ["msgs.delete_supportgroupmessage"],
    }


class GroupMessagesAPIView(ListCreateAPIView):
    serializer_class = SupportGroupMessageSerializer
    permission_classes = (
        IsPersonPermission,
        GroupMessagesPermissions,
    )
    pagination_class = APIPageNumberPagination
    required_membership_type = Membership.MEMBERSHIP_TYPE_FOLLOWER

    def check_permissions(self, request):
        super().check_permissions(request)
        self.check_object_permissions(request, self.supportgroup)

    def initial(self, request, *args, **kwargs):
        self.supportgroup = get_object_or_404(SupportGroup.objects.active(), **kwargs)
        super().initial(request, *args, **kwargs)

    def get_required_membership_type(self):
        return self.required_membership_type

    def get_queryset(self):
        person = self.request.user.person
        memberships = self.supportgroup.memberships.filter(person=person)
        user_permission = 0
        if memberships.exists():
            user_permission = memberships.first().membership_type

        # Messages where user is author or allowed
        return (
            self.supportgroup.messages.with_serializer_prefetch()
            .prefetch_related("comments")
            .active()
            .filter(Q(required_membership_type__lte=user_permission) | Q(author=person))
            .order_by("-created")
        )

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=self.serializer_class.LIST_FIELDS, **kwargs
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            message = serializer.save(
                author=self.request.user.person,
                supportgroup=self.supportgroup,
                required_membership_type=self.get_required_membership_type(),
            )

            new_message_notifications(message)
            update_recipient_message(message, self.request.user.person)


# Allow anyone to send private message
class GroupMessagesPrivateAPIView(GroupMessagesAPIView):
    permission_classes = (IsPersonPermission,)

    def get(self, *args, **kwargs):
        pass

    def get_required_membership_type(self):
        # Fallback to managers if the group has no referents
        return (
            Membership.MEMBERSHIP_TYPE_REFERENT
            if self.supportgroup.referents
            else Membership.MEMBERSHIP_TYPE_MANAGER
        )


# Get or set muted notification in recipient_mutedlist
class GroupMessageNotificationStatusAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        IsPersonPermission,
        GroupMessagesNotificationPermissions,
    )
    queryset = SupportGroupMessage.objects.all()

    def get(self, request, *args, **kwargs):
        message = self.get_object()
        person = self.request.user.person
        is_muted = SupportGroupMessageRecipient.filter(
            recipient=person, message=message, muted=True
        ).exists()
        return Response(is_muted)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        is_muted = request.data.get("isMuted", None)

        if not isinstance(is_muted, bool):
            raise ValidationError({"isMuted": "Ce champ est obligatoire"})

        person = self.request.user.person

        SupportGroupMessageRecipient.objects.update_or_create(
            message=message, recipient=person, defaults={"muted": is_muted}
        )

        return Response(is_muted)


# Get or set message locked
class GroupMessageLockedStatusAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        IsPersonPermission,
        GroupMessagesLockPermissions,
    )
    queryset = SupportGroupMessage.objects.all()

    def get(self, request, *args, **kwargs):
        message = self.get_object()
        return Response(message.is_locked)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        is_locked = request.data.get("isLocked", None)

        if not isinstance(is_locked, bool):
            raise ValidationError({"isLocked": "Ce champ est obligatoire"})

        message.is_locked = is_locked
        message.save()
        return Response(message.is_locked)


@method_decorator(never_cache, name="get")
class GroupSingleMessageAPIView(RetrieveUpdateDestroyAPIView):
    queryset = SupportGroupMessage.objects.active().annotate(
        last_update=Greatest(
            Max("comments__created"), "created", output_field=DateTimeField()
        )
    )
    serializer_class = SupportGroupMessageSerializer
    permission_classes = (
        IsPersonPermission,
        GroupMessagePermissions,
    )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_serializer_prefetch()
            .prefetch_related("comments")
        )

    def get_object(self):
        message = super().get_object()
        update_recipient_message(message, self.request.user.person)
        return message

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(
            *args, fields=self.serializer_class.DETAIL_FIELDS, **kwargs
        )

    def perform_update(self, serializer):
        with reversion.create_revision():
            super().perform_update(serializer)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()


class GroupMessageParticipantsAPIView(RetrieveAPIView):
    serializer_class = SupportGroupMessageParticipantSerializer
    permission_classes = (
        IsPersonPermission,
        GroupMessagePermissions,
    )
    queryset = SupportGroupMessage.objects.active()


class GroupMessageCommentsPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "POST": [], "PATCH": [], "PUT": [], "DELETE": []}
    object_perms_map = {
        "GET": ["msgs.view_supportgroupmessage"],
        "POST": ["msgs.add_supportgroupmessagecomment"],
        "PATCH": ["msgs.change_supportgroupmessagecomment"],
        "PUT": ["msgs.change_supportgroupmessagecomment"],
        "DELETE": ["msgs.delete_supportgroupmessagecomment"],
    }


class GroupMessageCommentsAPIView(ListCreateAPIView):
    serializer_class = MessageCommentSerializer
    permission_classes = (
        IsPersonPermission,
        GroupMessageCommentsPermissions,
    )
    pagination_class = APIPageNumberPagination

    def initial(self, request, *args, **kwargs):
        self.message = get_object_or_404(SupportGroupMessage.objects.active(), **kwargs)
        self.check_object_permissions(request, self.message)
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return (
            self.message.comments.with_serializer_prefetch()
            .active()
            .order_by("-created")
        )

    def perform_create(self, serializer):
        with transaction.atomic():
            comment = serializer.save(
                author=self.request.user.person, message=self.message
            )
            new_comment_notifications(comment)
            update_recipient_message(self.message, self.request.user.person)


class GroupSingleCommentAPIView(UpdateAPIView, DestroyAPIView):
    queryset = SupportGroupMessageComment.objects.with_serializer_prefetch().active()
    serializer_class = MessageCommentSerializer
    permission_classes = (
        IsPersonPermission,
        GroupMessageCommentsPermissions,
    )

    def perform_update(self, serializer):
        with reversion.create_revision():
            super().perform_update(serializer)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()


class JoinGroupAPIView(CreateAPIView, DestroyAPIView):
    permission_classes = (IsPersonPermission,)
    queryset = SupportGroup.objects.active()
    target_membership_type = Membership.MEMBERSHIP_TYPE_MEMBER

    def check_object_permissions(self, request, obj):
        if not obj.open:
            raise PermissionDenied(detail={"error_code": "full_group"})

        if obj.is_full:
            raise PermissionDenied(detail={"error_code": "full_group"})

    def create(self, request, *args, **kwargs):
        supportgroup = self.get_object()
        try:
            membership = Membership.objects.get(
                supportgroup=supportgroup,
                person=request.user.person,
            )
            if membership.membership_type == self.target_membership_type:
                return Response(status=status.HTTP_204_NO_CONTENT)
            membership.membership_type = self.target_membership_type
            membership.save()
            return Response(status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            with transaction.atomic():
                membership = Membership.objects.create(
                    supportgroup=supportgroup,
                    person=request.user.person,
                    membership_type=self.target_membership_type,
                )
                someone_joined_notification(
                    membership, membership_count=supportgroup.active_members_count
                )
            return Response(status=status.HTTP_201_CREATED)


class FollowGroupAPIView(JoinGroupAPIView):
    target_membership_type = Membership.MEMBERSHIP_TYPE_FOLLOWER

    def check_object_permissions(self, request, obj):
        if not obj.open:
            raise PermissionDenied(detail={"error_code": "full_group"})


class QuitGroupAPIView(DestroyAPIView):
    permission_classes = (IsPersonPermission,)
    queryset = SupportGroup.objects.all()

    def destroy(self, request, *args, **kwargs):
        supportgroup = self.get_object()

        membership = get_object_or_404(
            Membership.objects.all(),
            supportgroup=supportgroup,
            person=request.user.person,
        )

        if (
            membership.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT
            and not Membership.objects.filter(
                supportgroup=membership.supportgroup,
                membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
            )
            .exclude(id=membership.id)
            .exists()
        ):
            raise PermissionDenied(detail={"error_code": "group_last_referent"})

        membership.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupMembersViewPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": []}
    object_perms_map = {
        "GET": ["groups.change_supportgroup"],
    }


class GroupMembersAPIView(ListAPIView):
    permission_classes = (
        IsPersonPermission,
        GroupMembersViewPermissions,
    )
    queryset = SupportGroup.objects.all()
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return (
            Membership.objects.active()
            .with_serializer_prefetch()
            .filter(supportgroup_id=self.kwargs.get("pk"))
        )


class GroupUpdatePermission(GlobalOrObjectPermissions):
    perms_map = {"PUT": [], "PATCH": []}
    object_perms_map = {
        "PUT": ["groups.change_supportgroup"],
        "PATCH": ["groups.change_supportgroup"],
    }


class GroupInvitationPermission(GlobalOrObjectPermissions):
    perms_map = {"POST": []}
    object_perms_map = {
        "POST": ["groups.change_supportgroup"],
    }


class GroupUpdateAPIView(UpdateAPIView):
    permission_classes = (
        IsPersonPermission,
        GroupUpdatePermission,
    )
    queryset = SupportGroup.objects.all()
    serializer_class = SupportGroupUpdateSerializer

    def perform_update(self, serializer):
        with reversion.create_revision():
            reversion.set_user(self.request.user)
            reversion.set_comment("Modification")
            super().perform_update(serializer)


class GroupInvitationAPIView(GenericAPIView):
    queryset = SupportGroup.objects.all()
    permission_classes = (
        IsPersonPermission,
        GroupInvitationPermission,
    )

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        user_id = self.request.user.person.id
        email = request.data.get("email", "")
        if not email:
            raise exceptions.ValidationError(
                detail={"email": "L'adresse email ne peut être vide"},
                code="invalid_format",
            )

        try:
            validate_email(email)
        except:
            raise exceptions.ValidationError(
                detail={"email": "L'adresse email n'est pas valide"},
                code="invalid_format",
            )

        try:
            p = Person.objects.get_by_natural_key(email)
            Membership.objects.get(supportgroup=group, person=p)
        except (Person.DoesNotExist, Membership.DoesNotExist):
            pass
        else:
            raise exceptions.ValidationError(
                detail={"email": "Cette personne fait déjà partie de votre groupe !"},
                code="invalid_format",
            )

        invite_to_group.delay(group.pk, email, user_id)
        return Response(status=status.HTTP_201_CREATED)


class MemberPersonalInformationPermission(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
    }
    object_perms_map = {
        "GET": ["groups.view_member_personal_information"],
    }


class MemberPersonalInformationAPIView(RetrieveAPIView):
    queryset = Membership.objects.with_serializer_prefetch().active().all()
    permission_classes = (
        IsPersonPermission,
        MemberPersonalInformationPermission,
    )
    serializer_class = MemberPersonalInformationSerializer


class GroupMemberUpdatePermission(GlobalOrObjectPermissions):
    perms_map = {
        "PATCH": [],
    }
    object_perms_map = {
        "PATCH": ["groups.change_membership_type"],
    }


class GroupMemberUpdateAPIView(UpdateAPIView):
    queryset = Membership.objects.with_serializer_prefetch().active().all()
    permission_classes = (
        IsPersonPermission,
        GroupMemberUpdatePermission,
    )
    serializer_class = MembershipSerializer

    def check_request_data_permissions(self, request, obj):
        # Group manager can only change membership type for members / followers
        membershipType = request.data.get("membershipType", 0)
        user_should_be_at_least_referent = (
            membershipType is not None
            and membershipType >= Membership.MEMBERSHIP_TYPE_MANAGER
        ) or obj.membership_type >= Membership.MEMBERSHIP_TYPE_MANAGER
        if (
            user_should_be_at_least_referent
            and Membership.objects.get(
                person=request.user.person, supportgroup=obj.supportgroup
            ).membership_type
            < Membership.MEMBERSHIP_TYPE_REFERENT
        ):
            self.permission_denied(
                request,
                message=getattr("groups.change_membership_type", "message", None),
                code=getattr("groups.change_membership_type", "code", None),
            )

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        self.check_request_data_permissions(request, obj)


class GroupFinancePermission(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
    }
    object_perms_map = {
        "GET": ["groups.view_group_finance"],
    }


class GroupFinanceAPIView(GenericAPIView):
    queryset = SupportGroup.objects.all()
    permission_classes = (
        IsPersonPermission,
        GroupFinancePermission,
    )
    serializer_class = SupportGroupSerializer

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        allocation = get_supportgroup_balance(group)
        current_spending_requests = (
            SpendingRequest.objects.filter(group=group)
            .exclude(status=SpendingRequest.Status.PAID)
            .order_by("-modified")
            .only("id", "title", "status", "spending_date", "amount")
        )
        last_year = timezone.now() - relativedelta(years=1)
        past_spending_requests = (
            SpendingRequest.objects.filter(group=group)
            .filter(
                status=SpendingRequest.Status.PAID,
                modified__gte=last_year,
            )
            .order_by("-modified")
            .only("id", "title", "status", "spending_date", "amount")
        )
        spending_requests = [
            {
                "id": spending_request.id,
                "title": spending_request.title,
                "status": spending_request.status,
                "category": spending_request.category,
                "date": spending_request.spending_date,
                "amount": spending_request.amount,
            }
            for spending_request in current_spending_requests | past_spending_requests
        ]

        return Response(
            status=status.HTTP_200_OK,
            data={"allocation": allocation, "spendingRequests": spending_requests},
        )


class CreateSupportGroupExternalLinkPermissions(GlobalOrObjectPermissions):
    perms_map = {"POST": []}
    object_perms_map = {
        "POST": ["groups.change_supportgroup"],
    }


class CreateSupportGroupExternalLinkAPIView(CreateAPIView):
    queryset = SupportGroup.objects.all()
    permission_classes = (
        IsPersonPermission,
        CreateSupportGroupExternalLinkPermissions,
    )
    serializer_class = SupportGroupExternalLinkSerializer

    def create(self, request, *args, **kwargs):
        self.supportgroup = self.get_object()
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        with reversion.create_revision():
            reversion.set_user(self.request.user)
            reversion.set_comment("Création d'un lien externe")
            serializer.save(supportgroup=self.supportgroup)


class RetrieveUpdateDestroySupportGroupExternalLinkPermisns(GlobalOrObjectPermissions):
    perms_map = {"GET": [], "PUT": [], "PATCH": [], "DELETE": []}
    object_perms_map = {
        "GET": ["groups.view_supportgroup"],
        "PUT": ["groups.change_supportgroup"],
        "PATCH": ["groups.change_supportgroup"],
        "DELETE": ["groups.change_supportgroup"],
    }


class RetrieveUpdateDestroySupportGroupExternalLinkAPIView(
    RetrieveUpdateDestroyAPIView
):
    queryset = SupportGroupExternalLink.objects.all()
    permission_classes = (
        IsActionPopulaireClientPermission,
        RetrieveUpdateDestroySupportGroupExternalLinkPermisns,
    )
    serializer_class = SupportGroupExternalLinkSerializer

    def check_object_permissions(self, request, obj):
        return super().check_object_permissions(request, obj.supportgroup)

    def perform_update(self, serializer):
        with reversion.create_revision():
            reversion.set_user(self.request.user)
            reversion.set_comment("Modification d'un lien externe")
            return super().perform_update(serializer)

    def perform_destroy(self, instance):
        with reversion.create_revision():
            reversion.set_user(self.request.user)
            reversion.set_comment("Suppression d'un lien externe")
            return super().perform_destroy(instance)


class GroupUpdateOwnMembershipPermission(GlobalOrObjectPermissions):
    perms_map = {
        "PATCH": [],
    }
    object_perms_map = {
        "PATCH": ["groups.update_own_membership"],
    }


class GroupUpdateOwnMembershipAPIView(UpdateAPIView):
    queryset = Membership.objects.with_serializer_prefetch().active()
    permission_classes = (
        IsPersonPermission,
        GroupUpdateOwnMembershipPermission,
    )
    serializer_class = MembershipSerializer
    lookup_url_kwarg = "group_pk"
    lookup_field = "supportgroup_id"

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.person is not None:
            return self.queryset.filter(person=self.request.user.person)
        return self.queryset.none()


class GroupStatisticsAPIViewPermissions(GlobalOrObjectPermissions):
    perms_map = {"GET": []}
    object_perms_map = {
        "GET": ["groups.change_supportgroup"],
    }


class GroupStatisticsAPIView(RetrieveAPIView):
    queryset = SupportGroup.objects.active()
    permission_classes = (IsPersonPermission, GroupStatisticsAPIViewPermissions)

    def filter_by_period(self, queryset, period=None, field="created"):
        if period == "ever":
            return queryset

        if period == "month":
            date = datetime.date.today().replace(day=1)
            return queryset.filter(**{f"{field}__gte": date})

        if period == "year":
            date = datetime.date.today().replace(day=1, month=1)
            return queryset.filter(**{f"{field}__gte": date})

        if period == "last_month":
            end = datetime.date.today().replace(day=1)
            start = end - relativedelta(months=1)
            return queryset.filter(**{f"{field}__range": (start, end)})

        if period == "last_year":
            end = datetime.date.today().replace(day=1, month=1)
            start = end - relativedelta(years=1)
            return queryset.filter(**{f"{field}__range": (start, end)})

        return queryset

    def get_events(self, instance, period=None):
        return self.filter_by_period(
            instance.organized_events.public().past(), period=period, field="start_time"
        ).annotate(
            rsvp_count=Count("rsvps", filter=Q(rsvps__status=RSVP.Status.CONFIRMED)),
            duration=ExpressionWrapper(
                F("end_time") - F("start_time"),
                output_field=DurationField(),
            ),
            address=Concat(
                "location_name",
                Value("\n"),
                "location_address1",
                Value(", "),
                "location_zip",
                Value(" "),
                "location_city",
                output_field=CharField(),
            ),
        )

    def get_members(self, instance, period=None):
        return self.filter_by_period(
            instance.memberships.active(),
            period=period,
        )

    def get_messages(self, instance, period=None):
        return self.filter_by_period(
            instance.messages.active(),
            period=period,
        )

    def get_comments(self, instance, period=None):
        return self.filter_by_period(
            SupportGroupMessageComment.objects.active().filter(
                message__supportgroup_id=instance.id
            ),
            period=period,
        )

    def get_event_subtypes(self, events):
        most_used_event_subtypes = {
            subtype["subtype_id"]: subtype["count"]
            for subtype in events.values("subtype_id")
            .annotate(count=Count("subtype_id"))
            .order_by("-count")[:3]
        }
        event_subtypes = EventSubtype.objects.filter(
            id__in=list(most_used_event_subtypes.keys())
        )
        event_subtypes = sorted(
            [
                {
                    **DisplayEventSubtypeSerializer(subtype).data,
                    "events": most_used_event_subtypes[subtype.id],
                }
                for subtype in event_subtypes
            ],
            key=lambda s: -s["events"],
        )

        return event_subtypes

    def get_event_locations(self, events):
        return (
            events.values("address")
            .annotate(events=Count("address"))
            .order_by("-events")[:3]
        )

    def get_event_average_by_month(self, events):
        events = events.order_by("start_time")
        event_count = len(events)

        if event_count == 0:
            return 0, 0

        start = events[0].start_time
        end = datetime.datetime.now()
        month_count = (end.year - start.year) * 12 + (end.month - start.month)

        return event_count, event_count / month_count

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        period = request.GET.get("period", None)

        events = self.get_events(instance, period)
        members = self.get_members(instance, period)
        messages = self.get_messages(instance, period)
        comments = self.get_comments(instance, period)

        event_count, event_average_count_by_month = self.get_event_average_by_month(
            events
        )

        data = {
            "events": {
                "count": event_count,
                "averageByMonth": event_average_count_by_month,
                "averageParticipants": 0,
                "totalDuration": 0,
                "averageDuration": 0,
                "topSubtypes": [],
                "topLocations": [],
            },
            "members": {
                "active": len([m for m in members if m.is_active_member]),
                "followers": len([m for m in members if not m.is_active_member]),
            },
            "messages": {"count": messages.count() + comments.count()},
        }
        if event_count > 0:
            aggregates = events.aggregate(
                average_rsvps=Avg("rsvp_count"),
                total_duration=Sum("duration"),
                average_duration=Avg("duration"),
            )
            data["events"]["averageParticipants"] = aggregates.get("average_rsvps")
            data["events"]["totalDuration"] = aggregates.get("total_duration")
            data["events"]["averageDuration"] = aggregates.get("average_duration")
            data["events"]["topSubtypes"] = self.get_event_subtypes(events)
            data["events"]["topLocations"] = self.get_event_locations(events)

        return Response(data)
