from rest_framework.generics import RetrieveUpdateAPIView, RetrieveAPIView, ListAPIView

from .. import serializers, models, permissions
from ...events.models import Event
from ...events.views.api_views import EventListAPIView
from ...lib.rest_framework_permissions import (
    IsPersonPermission,
)

__all__ = [
    "EventSpeakerRetrieveUpdateAPIView",
    "EventSpeakerRequestRetrieveUpdateAPIView",
    "EventSpeakerEventListAPIView",
]


class EventSpeakerRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        IsPersonPermission,
        permissions.EventSpeakerAPIPermissions,
    )
    queryset = models.EventSpeaker.objects.all().with_serializer_prefetch()
    lookup_field = "person_id"
    serializer_class = serializers.EventSpeakerSerializer

    def get_object(self):
        self.kwargs[self.lookup_field] = self.request.user.person.id
        return super().get_object()


class EventSpeakerRequestRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        IsPersonPermission,
        permissions.EventSpeakerRequestAPIPermissions,
    )
    queryset = models.EventSpeakerRequest.objects.all().select_related("event_request")
    serializer_class = serializers.EventSpeakerRequestSerialier


class EventSpeakerEventListAPIView(EventListAPIView):
    def get_queryset(self):
        queryset = super().get_queryset()
        event_speaker = self.request.user.person.event_speaker
        if event_speaker is None:
            return queryset.none()
        return event_speaker.get_upcoming_events(queryset=queryset).order_by(
            "start_time"
        )