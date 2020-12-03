import ics
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import (
    HttpResponseGone,
    HttpResponseForbidden,
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponse,
    Http404,
)
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, DeleteView, FormView, ListView

from agir.authentication.view_mixins import (
    GlobalOrObjectPermissionRequiredMixin,
    HardLoginRequiredMixin,
)
from agir.front.view_mixins import ObjectOpengraphMixin, FilterView
from agir.groups.filters import GroupFilterSet
from agir.groups.forms import ExternalJoinForm
from agir.groups.models import SupportGroup, Membership, SupportGroupSubtype
from agir.groups.tasks import send_someone_joined_notification
from agir.lib.utils import front_url
from agir.people.actions.subscription import SUBSCRIPTION_TYPE_EXTERNAL
from agir.people.views import ConfirmSubscriptionView

__all__ = [
    "SupportGroupListView",
    "SupportGroupDetailView",
    "SupportGroupIcsView",
    "QuitSupportGroupView",
    "ExternalJoinSupportGroupView",
    "ThematicTeamsViews",
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

    def dispatch(self, request, *args, **kwargs):
        if (
            self.request.user.is_authenticated
            and hasattr(self.request.user, "person")
            and request.user.person.is_2022_only
        ):
            self.queryset = self.queryset.is_2022()

        return super().dispatch(request, *args, **kwargs)


class SupportGroupDetailView(
    ObjectOpengraphMixin, GlobalOrObjectPermissionRequiredMixin, DetailView
):
    permission_required = ("groups.view_supportgroup",)
    template_name = "groups/detail.html"
    model = SupportGroup

    title_prefix = "Groupe"
    meta_description = "Rejoignez les groupes d'action de la France insoumise."
    meta_description_2022 = "Rejoignez les groupes de soutien de votre quartier pour la candidature de Jean-Luc Mélenchon pour 2022"

    def handle_no_permission(self):
        return HttpResponseGone()

    def get_template_names(self):
        return ["groups/detail.html"]

    def get_context_data(self, **kwargs):
        events_future = Paginator(
            self.object.organized_events.upcoming().distinct().order_by("start_time"), 5
        ).get_page(self.request.GET.get("events_future_page"))
        events_past = Paginator(
            self.object.organized_events.past().distinct().order_by("-start_time"), 5
        ).get_page(self.request.GET.get("events_past_page"))

        return super().get_context_data(
            events_future=events_future,
            events_past=events_past,
            is_member=self.request.user.is_authenticated
            and self.object.memberships.filter(
                person=self.request.user.person
            ).exists(),
            **kwargs,
        )

    @method_decorator(login_required(login_url=reverse_lazy("short_code_login")))
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not request.user.person.is_insoumise and not self.object.allow_external:
            return HttpResponseForbidden()

        if request.POST["action"] == "join":
            try:
                membership = Membership.objects.create(
                    supportgroup=self.object, person=request.user.person
                )
                send_someone_joined_notification.delay(membership.pk)
            except IntegrityError:
                pass  # the person is already a member of the group
            return HttpResponseRedirect(
                reverse("view_group", kwargs={"pk": self.object.pk})
            )

        return HttpResponseBadRequest()


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


class ExternalJoinSupportGroupView(ConfirmSubscriptionView, FormView, DetailView):
    queryset = SupportGroup.objects.filter(subtypes__allow_external=True)
    form_class = ExternalJoinForm
    show_already_created_message = False
    default_type = SUBSCRIPTION_TYPE_EXTERNAL

    def dispatch(self, request, *args, **kwargs):
        self.group = self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def success_page(self, params):
        if Membership.objects.filter(
            person=self.person, supportgroup=self.group
        ).exists():
            messages.add_message(
                request=self.request,
                level=messages.INFO,
                message=_("Vous êtes déjà membre."),
            )
            return HttpResponseRedirect(reverse("view_group", args=[self.group.pk]))

        Membership.objects.get_or_create(person=self.person, supportgroup=self.group)
        messages.add_message(
            request=self.request,
            level=messages.INFO,
            message=_("Vous avez bien rejoint le groupe."),
        )

        return HttpResponseRedirect(reverse("view_group", args=[self.group.pk]))

    def form_valid(self, form):
        form.send_confirmation_email(self.group)
        messages.add_message(
            request=self.request,
            level=messages.INFO,
            message=_(
                "Un email vous a été envoyé. Merrci de cliquer sur le "
                "lien qu'il contient pour confirmer."
            ),
        )
        return HttpResponseRedirect(reverse("view_group", args=[self.group.pk]))

    def form_invalid(self, form):
        return HttpResponseRedirect(reverse("view_group", args=[self.group.pk]))


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
