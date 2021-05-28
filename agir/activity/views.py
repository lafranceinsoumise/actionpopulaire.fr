from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from rest_framework import status
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from agir.activity.actions import (
    get_activities,
    get_non_custom_announcements,
    get_custom_announcements,
)
from agir.activity.models import Activity, Announcement
from agir.activity.serializers import (
    ActivitySerializer,
    ActivityStatusUpdateRequest,
    AnnouncementSerializer,
    CustomAnnouncementSerializer,
)
from agir.lib.rest_framework_permissions import (
    GlobalOrObjectPermissions,
    IsPersonPermission,
)


class ActivityAPIView(RetrieveUpdateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (
        IsAuthenticated,
        GlobalOrObjectPermissions,
    )


class UserActivitiesAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ActivitySerializer

    def get_queryset(self):
        # Force creation of new non_custom announcement activities for the user
        get_non_custom_announcements(self.request.user.person)
        return get_activities(self.request.user.person)


class AnnouncementsAPIView(ListAPIView):
    permission_classes = ()
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
    permission_classes = (IsAuthenticated,)
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
        return (
            get_custom_announcements(self.request.user.person)
            .order_by("custom_display", "-priority", "-start_date", "end_date")
            .distinct("custom_display")
        )


class AnnouncementLinkView(DetailView):
    model = Announcement
    queryset = Announcement.objects.all()

    def get(self, request, *args, **kwargs):
        announcement = self.get_object()
        user = request.user
        if hasattr(user, "person"):
            Activity.objects.update_or_create(
                recipient=user.person,
                announcement=announcement,
                defaults={
                    "type": Activity.TYPE_ANNOUNCEMENT,
                    "status": Activity.STATUS_INTERACTED,
                },
            )
        return HttpResponseRedirect(announcement.link)


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
