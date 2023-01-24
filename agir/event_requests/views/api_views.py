from rest_framework.generics import RetrieveUpdateAPIView

from .. import serializers
from ..models import EventSpeaker
from ...lib.rest_framework_permissions import (
    GlobalOrObjectPermissions,
    IsPersonPermission,
)

__all__ = [
    "EventSpeakerRetrieveUpdateAPIView",
]


class EventSpeakerAPIPermissions(GlobalOrObjectPermissions):
    perms_map = {
        "GET": [],
        "PATCH": [],
        "PUT": [],
    }
    object_perms_map = {
        "GET": ["event_requests.view_event_speaker"],
        "PATCH": ["event_requests.change_event_speaker"],
        "PUT": ["event_requests.change_event_speaker"],
    }


class EventSpeakerRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = serializers.EventSpeakerSerializer
    queryset = EventSpeaker.objects.all()
    permission_classes = (
        IsPersonPermission,
        EventSpeakerAPIPermissions,
    )
    lookup_field = "person_id"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related(
                "event_themes",
                "event_themes__event_theme_type",
                "event_speaker_requests",
                "event_speaker_requests__event_request",
            )
        )

    def get_object(self):
        self.kwargs[self.lookup_field] = self.request.user.person.id
        return super().get_object()
