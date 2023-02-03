from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404
from django.views.generic.detail import BaseDetailView

from agir.authentication.view_mixins import GlobalOrObjectPermissionRequiredMixin
from agir.event_requests.models import EventSpeaker


class EventSpeakerViewMixin(GlobalOrObjectPermissionRequiredMixin, BaseDetailView):
    permission_required = ("event_requests.view_event_speaker",)
    queryset = EventSpeaker.objects.all()

    def handle_no_permission(self):
        return redirect_to_login(self.request.get_full_path())

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        return get_object_or_404(queryset, person_id=self.request.user.person.id)
