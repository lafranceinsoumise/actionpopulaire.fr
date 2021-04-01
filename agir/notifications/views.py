from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from agir.notifications.serializers import WebPushSubscriptionSerializer


class WebPushSubscriptionAPIView(CreateAPIView):
    serializer_class = WebPushSubscriptionSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(person=self.request.user.person)
