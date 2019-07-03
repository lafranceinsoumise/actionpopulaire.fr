from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from agir.notifications.models import Notification


class FollowNotificationView(DetailView):
    model = Notification
    queryset = Notification.objects.select_related("announcement")

    def get(self, request, *args, **kwargs):
        notification = self.get_object()

        if notification.status != Notification.STATUS_CLICKED:
            notification.status = Notification.STATUS_CLICKED
            notification.save()

        return HttpResponseRedirect(notification.link or notification.announcement.link)


class NotificationsSerializer(serializers.Serializer):
    notifications = serializers.PrimaryKeyRelatedField(
        queryset=Notification.objects.all(), many=True
    )


class NotificationsSeenView(GenericAPIView):
    permission_classes = ()

    serializer_class = NotificationsSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.person:
            raise PermissionDenied(detail="Pas authentifié", code="unauthenticated")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Notification.objects.filter(
            status=Notification.STATUS_UNSEEN, id__in=serializer.data["notifications"]
        ).update(status=Notification.STATUS_SEEN)

        return Response(data={"code": "ok"}, status=200)
