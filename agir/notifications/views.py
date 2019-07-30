from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from agir.lib.permissions import IsPersonPermission
from agir.notifications.actions import serialize_notifications
from agir.notifications.models import Notification
from agir.notifications.serializers import (
    NotificationIdsSerializer,
    ParametersSerializer,
)


class FollowNotificationView(DetailView):
    model = Notification
    queryset = Notification.objects.select_related("announcement")

    def get(self, request, *args, **kwargs):
        notification = self.get_object()

        if notification.status != Notification.STATUS_CLICKED:
            notification.status = Notification.STATUS_CLICKED
            notification.save()

        return HttpResponseRedirect(notification.link or notification.announcement.link)


class NotificationsSeenView(GenericAPIView):
    permission_classes = ()

    serializer_class = NotificationIdsSerializer

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.person:
            raise PermissionDenied(detail="Pas authentifié", code="unauthenticated")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Notification.objects.filter(
            status=Notification.STATUS_UNSEEN, id__in=serializer.data["notifications"]
        ).update(status=Notification.STATUS_SEEN)

        return Response(data={"code": "ok"}, status=200)


class NotificationsView(GenericAPIView):
    queryset = Notification.objects.all()

    permission_classes = (IsPersonPermission,)

    def get(self, request, *args, **kwargs):
        parameters = ParametersSerializer(
            data=request.query_params, context=self.get_serializer_context()
        )

        if parameters.is_valid():
            print(parameters.validated_data)

            length = parameters.validated_data["length"]
            offset = parameters.validated_data["offset"]

            notifications = (
                self.get_queryset()
                .filter(person=request.user.person)
                .select_related("announcement")[offset : (offset + length)]
            )

            return Response(data=serialize_notifications(notifications))

        else:
            return Response(data=[], status=400)
