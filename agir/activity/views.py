from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import DetailView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.response import Response

from agir.activity.actions import (
    get_activities,
    get_non_custom_announcements,
    get_custom_announcements,
)
from agir.activity.models import Activity, Announcement, PushAnnouncement
from agir.activity.serializers import (
    ActivitySerializer,
    ActivityStatusUpdateRequest,
    AnnouncementSerializer,
    CustomAnnouncementSerializer,
)
from agir.api import settings
from agir.lib.pagination import APIPageNumberPagination
from agir.lib.rest_framework_permissions import (
    GlobalOrObjectPermissions,
    IsPersonPermission,
    IsActionPopulaireClientPermission,
)
from agir.lib.utils import front_url


class ActivityAPIView(RetrieveUpdateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (
        IsPersonPermission,
        GlobalOrObjectPermissions,
    )


class UserActivitiesAPIView(ListAPIView):
    permission_classes = (IsPersonPermission,)
    serializer_class = ActivitySerializer
    pagination_class = APIPageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            self.check_activity_permissions(page)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        self.check_activity_permissions(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def check_activity_permissions(self, queryset):
        # Double-check permissions for embedded event / supportgroup
        # and raise an error if needed
        for activity in queryset:
            assert self.request.user.has_perm("activity.view_activity", activity)

    def get_queryset(self):
        # Force creation of new non_custom announcement activities for the user
        get_non_custom_announcements(self.request.user.person)
        return get_activities(self.request.user.person)


class AnnouncementsAPIView(ListAPIView):
    permission_classes = (IsActionPopulaireClientPermission,)
    serializer_class = AnnouncementSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.person is not None:
            announcements = get_non_custom_announcements(self.request.user.person)
            # Automatically mark related activities if mark_as_displayed query param equals "1"
            if self.request.GET.get("mark_as_displayed", "0") == "1":
                Activity.objects.filter(
                    pk__in=[a.activity_id for a in announcements if a.activity_id],
                    status=Activity.STATUS_UNDISPLAYED,
                ).update(status=Activity.STATUS_DISPLAYED)

            return announcements
        return get_non_custom_announcements()


class UserCustomAnnouncementAPIView(RetrieveAPIView):
    permission_classes = (IsPersonPermission,)
    serializer_class = CustomAnnouncementSerializer
    lookup_field = "custom_display"

    def get_object(self):
        announcement = super().get_object()
        if announcement.activity_id:
            Activity.objects.filter(
                pk=announcement.activity_id, status=Activity.STATUS_UNDISPLAYED
            ).update(status=Activity.STATUS_DISPLAYED)
        return announcement

    def get_queryset(self):
        return get_custom_announcements(
            self.request.user.person, self.kwargs.get(self.lookup_field, None)
        )


class AnnouncementLinkView(DetailView):
    model = Announcement
    queryset = Announcement.objects.all()

    def get(self, request, *args, **kwargs):
        announcement = self.get_object()
        user = request.user
        if hasattr(user, "person"):
            defaults = {
                "type": Activity.TYPE_ANNOUNCEMENT,
                "status": Activity.STATUS_INTERACTED,
            }
            activity = Activity.objects.filter(
                recipient=user.person, announcement=announcement
            ).first()
            if activity is not None:
                for key, value in defaults.items():
                    setattr(activity, key, value)
                activity.save()
            else:
                Activity.objects.create(
                    recipient=user.person, announcement=announcement, **defaults
                )

        return HttpResponseRedirect(announcement.link)


class PushAnnouncementLinkView(DetailView):
    model = PushAnnouncement
    queryset = PushAnnouncement.objects.all()

    def get(self, request, *args, **kwargs):
        push_announcement = self.get_object()
        user = request.user

        if (
            user.is_authenticated
            and hasattr(user, "person")
            and user.person is not None
        ):
            Activity.objects.update_or_create(
                type=Activity.TYPE_PUSH_ANNOUNCEMENT,
                recipient=user.person,
                push_announcement=push_announcement,
                defaults={
                    "push_status": Activity.STATUS_INTERACTED,
                },
            )

        return HttpResponseRedirect(push_announcement.link)


class ActivityStatusUpdateView(GenericAPIView):
    serializer_class = ActivityStatusUpdateRequest
    permission_classes = (IsPersonPermission,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        status_order = [s for s, _ in Activity.STATUS_CHOICES]
        lower_statuses = status_order[
            : status_order.index(serializer.validated_data["status"])
        ]

        Activity.objects.filter(
            recipient=request.user.person,  # pour ne laisser la possibilité de modifier que ses propres activités
            status__in=lower_statuses,
            id__in=serializer.validated_data["ids"],
        ).update(status=serializer.validated_data["status"])

        return Response(None, status=status.HTTP_204_NO_CONTENT)


# Mark as displayed all undisplayed activities of current user
class ActivityStatusUpdateAllReadView(RetrieveAPIView):
    serializer_class = ActivityStatusUpdateRequest
    permission_classes = (IsPersonPermission,)

    def get(self, request, *args, **kwargs):
        Activity.objects.filter(
            recipient=request.user.person, status=Activity.STATUS_UNDISPLAYED
        ).update(status=Activity.STATUS_DISPLAYED)
        return Response(None, status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes((IsActionPopulaireClientPermission,))
def get_unread_activity_count(request):
    unread_activity_count = 0
    if request.user.is_authenticated and request.user.person is not None:
        unread_activity_count = (
            get_activities(request.user.person)
            .filter(status=Activity.STATUS_UNDISPLAYED)
            .count()
        )

    return Response({"unreadActivityCount": unread_activity_count})


@api_view(["GET"])
@permission_classes(())
def follow_activity_link(request, pk):
    user = request.user
    if user.is_authenticated and user.person is not None:
        try:
            activity = Activity.objects.get(pk=pk, recipient=user.person)
            activity.status = Activity.STATUS_INTERACTED
            activity.save()
        except Activity.DoesNotExist:
            pass

    next = request.GET.get("next", front_url("list_activities"))
    allowed_hosts = {
        s.strip("/").rsplit("/", 1)[-1]
        for s in [
            settings.MAIN_DOMAIN,
            settings.API_DOMAIN,
            settings.FRONT_DOMAIN,
            settings.NSP_DOMAIN,
            "https://infos.actionpopulaire.fr",
        ]
    }
    url_is_safe = url_has_allowed_host_and_scheme(
        url=next,
        allowed_hosts=allowed_hosts,
        require_https=True,
    )
    if not url_is_safe:
        next = front_url("list_activities")

    return HttpResponseRedirect(next)
