from django.http import HttpResponseRedirect
from django.views.generic import DetailView
from rest_framework.generics import RetrieveUpdateAPIView

from agir.activity.models import Activity, Announcement
from agir.activity.serializers import ActivitySerializer
from agir.lib.rest_framework_permissions import GlobalOrObjectPermissions


class ActivityAPIView(RetrieveUpdateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (GlobalOrObjectPermissions,)


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
