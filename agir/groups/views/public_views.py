import ics
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.http import (
    HttpResponseGone,
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponse,
    Http404,
)
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.generic import DetailView, DeleteView, ListView

from agir.authentication.view_mixins import (
    GlobalOrObjectPermissionRequiredMixin,
    HardLoginRequiredMixin,
)
from agir.front.view_mixins import FilterView
from agir.groups.actions.notifications import someone_joined_notification
from agir.groups.filters import GroupFilterSet
from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.lib.utils import front_url

__all__ = [
    "SupportGroupListView",
    "SupportGroupIcsView",
    "QuitSupportGroupView",
    "ThematicTeamsViews",
    "SupportGroupDetailMixin",
]


class SupportGroupListView(FilterView):
    """List of groups, filter by zipcode
    """

    min_items = 20
    template_name = "groups/group_list.html"
    context_object_name = "groups"
    paginate_by = 20
    queryset = SupportGroup.objects.filter(published=True)
    filter_class = GroupFilterSet


class SupportGroupIcsView(DetailView):
    queryset = SupportGroup.objects.active().all()

    def render_to_response(self, context, **response_kwargs):
        calendar = ics.Calendar(
            events=[
                ics.event.Event(
                    name=event.name,
                    begin=event.start_time,
                    end=event.end_time,
                    uid=str(event.pk),
                    description=event.description,
                    location=event.short_address,
                    url=front_url("view_event", args=[event.pk], auto_login=False),
                )
                for event in context["supportgroup"].organized_events.all()
            ]
        )

        return HttpResponse(calendar, content_type="text/calendar")


@method_decorator(never_cache, name="get")
class QuitSupportGroupView(
    HardLoginRequiredMixin, GlobalOrObjectPermissionRequiredMixin, DeleteView
):
    template_name = "groups/quit.html"
    success_url = reverse_lazy("dashboard")
    queryset = Membership.objects.active().all()
    permission_required = ("groups.delete_membership",)
    context_object_name = "membership"

    def get_object(self, queryset=None):
        try:
            return (
                self.get_queryset()
                .select_related("supportgroup")
                .get(
                    supportgroup__pk=self.kwargs["pk"], person=self.request.user.person
                )
            )
        except Membership.DoesNotExist:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.object.supportgroup
        context["success_url"] = self.get_success_url()
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        self.object.delete()

        messages.add_message(
            request,
            messages.SUCCESS,
            format_html(
                _("Vous avez bien quitté le groupe <em>{}</em>"),
                self.object.supportgroup.name,
            ),
        )

        return HttpResponseRedirect(success_url)


class ThematicTeamsViews(ListView):
    template_name = "groups/thematic_teams.html"
    context_object_name = "groups"

    def get_queryset(self):
        subtype = SupportGroupSubtype.objects.get(label="rédaction du livret")
        return SupportGroup.objects.active().filter(subtypes=subtype).order_by("name")

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs, default_image="front/images/AEC-mini.png"
        )


class SupportGroupDetailMixin(GlobalOrObjectPermissionRequiredMixin):
    permission_required = ("groups.view_supportgroup",)
    meta_description = "Rejoignez les groupes d'action de la France insoumise."
    meta_description_2022 = "Rejoignez les équipes de soutien de votre quartier pour la candidature de Jean-Luc Mélenchon pour 2022"
    queryset = SupportGroup.objects.all()
    bundle_name = "front/app"
    data_script_id = "exportedGroup"

    def handle_no_permission(self):
        return HttpResponseGone()

    def can_join(self):
        if self.object.is_2022:
            return self.request.user.person.is_2022
        return self.request.user.person.is_insoumise

    @method_decorator(login_required(login_url=reverse_lazy("short_code_login")))
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.can_join():
            return HttpResponseRedirect(
                f'{reverse("join")}?type={"2" if self.object.is_2022 else "I"}'
            )

        if request.POST["action"] == "join":
            if self.object.is_full:
                return HttpResponseRedirect(
                    reverse("full_group", kwargs={"pk": self.object.pk})
                )
            try:
                with transaction.atomic():
                    membership = Membership.objects.create(
                        supportgroup=self.object, person=request.user.person
                    )
                    someone_joined_notification(
                        membership, membership_count=self.object.members_count
                    )
            except IntegrityError:
                pass  # the person is already a member of the group
            return HttpResponseRedirect(
                reverse("view_group", kwargs={"pk": self.object.pk})
            )

        return HttpResponseBadRequest()
