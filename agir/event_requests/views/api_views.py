from rest_framework.generics import RetrieveUpdateAPIView

from .. import serializers, models, permissions
from ...lib.rest_framework_permissions import (
    IsPersonPermission,
)

__all__ = [
    "EventSpeakerRetrieveUpdateAPIView",
    "EventSpeakerRequestRetrieveUpdateAPIView",
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
