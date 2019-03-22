from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from agir.authentication.models import Role
from agir.notifications.models import Notification, NotificationStatus


class FollowNotificationView(DetailView):
    model = Notification

    def get(self, request, *args, **kwargs):
        self.notification = self.get_object()

        if request.user.is_authenticated and request.user.type == Role.PERSON_ROLE:
            try:
                notification = NotificationStatus.objects.get(
                    notification=self.notification, person=request.user.person
                )
            except NotificationStatus.DoesNotExist:
                notification = NotificationStatus(
                    notification=self.notification, person=request.user.person
                )

            if notification.status != NotificationStatus.STATUS_CLICKED:
                notification.status = NotificationStatus.STATUS_CLICKED
                notification.save()

        return HttpResponseRedirect(self.notification.link)


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

        person = request.user.person

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for id in serializer.data["notifications"]:
            NotificationStatus.objects.get_or_create(
                person=person,
                notification_id=id,
                defaults={"status": NotificationStatus.STATUS_SEEN},
            )

        return Response(data={"code": "ok"}, status=200)
