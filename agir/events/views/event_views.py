import json

import ics
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import (
    CreateView,
    UpdateView,
    TemplateView,
    DeleteView,
    DetailView,
)
from django.views.generic.edit import ProcessFormView, FormMixin
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from django.utils.translation import ugettext as _

from agir.events.actions.legal import QUESTIONS
from ..models import Event, RSVP, Calendar, EventSubtype
from ..tasks import send_cancellation_notification

from ..forms import (
    EventForm,
    AddOrganizerForm,
    EventGeocodingForm,
    EventReportForm,
    UploadEventImageForm,
    AuthorForm,
    SearchEventForm,
)
from agir.front.view_mixins import (
    ObjectOpengraphMixin,
    ChangeLocationBaseView,
    SearchByZipcodeBaseView,
)
from agir.authentication.view_mixins import (
    HardLoginRequiredMixin,
    PermissionsRequiredMixin,
    SoftLoginRequiredMixin,
)

__all__ = [
    "CreateEventView",
    "ManageEventView",
    "ModifyEventView",
    "QuitEventView",
    "CancelEventView",
    "EventDetailView",
    "EventIcsView",
    "CalendarView",
    "CalendarIcsView",
    "ChangeEventLocationView",
    "EditEventReportView",
    "UploadEventImageView",
    "EventListView",
    "PerformCreateEventView",
]


class EventListView(SearchByZipcodeBaseView):
    """List of events, filter by zipcode
    """

    template_name = "events/event_list.html"
    context_object_name = "events"
    form_class = SearchEventForm

    def get_base_queryset(self):
        return Event.objects.upcoming().order_by("start_time")


class EventDetailView(ObjectOpengraphMixin, PermissionsRequiredMixin, DetailView):
    template_name = "events/detail.html"
    permissions_required = ("events.view_event",)
    permission_denied_to_not_found = True
    model = Event

    title_prefix = _("Evénement local")
    meta_description = _(
        "Participez aux événements organisés par les membres de la France insoumise."
    )

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            rsvp=self.request.user.is_authenticated
            and self.object.rsvps.filter(person=self.request.user.person).first(),
            is_organizer=self.request.user.is_authenticated
            and self.object.organizers.filter(pk=self.request.user.person.id).exists(),
            organizers_groups=self.object.organizers_groups.distinct(),
            event_images=self.object.images.all(),
        )


class EventIcsView(PermissionsRequiredMixin, DetailView):
    model = Event
    permissions_required = ("events.view_event",)
    permission_denied_to_not_found = True

    def render_to_response(self, context, **response_kwargs):
        ics_calendar = ics.Calendar(events=[context["event"].to_ics()])

        return HttpResponse(ics_calendar, content_type="text/calendar")


class ManageEventView(HardLoginRequiredMixin, PermissionsRequiredMixin, DetailView):
    template_name = "events/manage.html"
    permissions_required = ("events.change_event",)
    model = Event

    error_messages = {
        "denied": _(
            "Vous ne pouvez pas accéder à cette page sans être organisateur de l'événement."
        )
    }

    def get_success_url(self):
        return reverse("manage_event", kwargs={"pk": self.object.pk})

    def get_form(self):
        kwargs = {}

        if self.request.method in ("POST", "PUT"):
            kwargs.update({"data": self.request.POST})

        return AddOrganizerForm(self.object, **kwargs)

    def get_context_data(self, **kwargs):
        if "add_organizer_form" not in kwargs:
            kwargs["add_organizer_form"] = self.get_form()

        return super().get_context_data(
            is_organizer=self.request.user.is_authenticated
            and self.object.organizers.filter(pk=self.request.user.person.id).exists(),
            organizers=self.object.organizers.all(),
            rsvps=self.object.rsvps.all(),
            **kwargs
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.is_past():
            raise PermissionDenied(
                _("Vous ne pouvez pas ajouter d'organisateur à un événement terminé.")
            )

        form = self.get_form()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(self.get_success_url())

        return self.render_to_response(self.get_context_data(add_organizer_form=form))


class CreateEventView(SoftLoginRequiredMixin, TemplateView):
    template_name = "events/create.html"

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        groups = [
            {"id": str(m.supportgroup.pk), "name": m.supportgroup.name}
            for m in person.memberships.filter(
                supportgroup__published=True, is_manager=True
            )
        ]

        initial = {"email": person.email}

        if person.contact_phone:
            initial["phone"] = person.contact_phone.as_e164

        if person.first_name and person.last_name:
            initial["name"] = "{} {}".format(person.first_name, person.last_name)

        initial_group = self.request.GET.get("group")
        if initial_group in [g["id"] for g in groups]:
            initial["organizerGroup"] = initial_group

        subtype_queryset = EventSubtype.objects.filter(
            visibility=EventSubtype.VISIBILITY_ALL
        )

        if "subtype" in self.request.GET:
            try:
                subtype = subtype_queryset.get(label=self.request.GET["subtype"])
                initial["subtype"] = subtype.label
            except EventSubtype.DoesNotExist:
                pass

        types = [
            {
                "id": id,
                "label": str(label),
                "description": str(EventSubtype.TYPE_DESCRIPTION[id]),
            }
            for id, label in EventSubtype.TYPE_CHOICES
        ]

        subtypes = [
            {"id": s.id, "label": s.label, "description": s.description, "type": s.type}
            for s in subtype_queryset
        ]

        questions = QUESTIONS

        return super().get_context_data(
            props=mark_safe(
                json.dumps(
                    {
                        "initial": initial,
                        "groups": groups,
                        "types": types,
                        "subtypes": subtypes,
                        "questions": questions,
                    }
                )
            ),
            **kwargs
        )


class PerformCreateEventView(SoftLoginRequiredMixin, FormMixin, ProcessFormView):
    model = Event
    form_class = EventForm

    def get_form_kwargs(self):
        """Add user person profile to the form kwargs"""

        kwargs = super().get_form_kwargs()

        person = self.request.user.person
        kwargs["person"] = person
        return kwargs

    def form_invalid(self, form):
        return JsonResponse({"errors": form.errors}, status=400)

    def form_valid(self, form):
        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message="Votre événement a été correctement créé.",
        )

        form.save()

        return JsonResponse(
            {
                "status": "OK",
                "id": form.instance.id,
                "url": reverse("view_event", args=[form.instance.id]),
            }
        )


class ModifyEventView(HardLoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    permissions_required = ("events.change_event",)
    template_name = "events/modify.html"
    form_class = EventForm

    def get_success_url(self):
        return reverse("manage_event", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now(), published_only=False)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["person"] = self.request.user.person
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Modifiez votre événement")
        return context

    def form_valid(self, form):
        # first get response to make sure there's no error when saving the model before adding message
        res = super().form_valid(form)

        messages.add_message(
            request=self.request,
            level=messages.SUCCESS,
            message=format_html(
                _("Les modifications de l'événement <em>{}</em> ont été enregistrées."),
                self.object.name,
            ),
        )

        return res


class CancelEventView(HardLoginRequiredMixin, PermissionsRequiredMixin, DetailView):
    permissions_required = ("events.change_event",)
    template_name = "events/cancel.html"
    success_url = reverse_lazy("list_events")

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now(), published_only=False)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.published = False
        self.object.save()

        send_cancellation_notification.delay(self.object.pk)

        messages.add_message(
            request,
            messages.WARNING,
            _("L'événement « {} » a bien été annulé.").format(self.object.name),
        )

        return HttpResponseRedirect(self.success_url)


class QuitEventView(SoftLoginRequiredMixin, PermissionsRequiredMixin, DeleteView):
    template_name = "events/quit.html"
    success_url = reverse_lazy("dashboard")
    context_object_name = "rsvp"

    def get_queryset(self):
        return RSVP.objects.filter(event__end_time__gte=timezone.now())

    def get_object(self, queryset=None):
        try:
            rsvp = (
                self.get_queryset()
                .select_related("event")
                .get(event__pk=self.kwargs["pk"], person=self.request.user.person)
            )
            if not self.request.user.has_perm("events.view_event", rsvp.event):
                raise Http404
        except RSVP.DoesNotExist:
            raise Http404()

        return rsvp

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.object.event
        context["success_url"] = self.get_success_url()
        return context

    def delete(self, request, *args, **kwargs):
        # first get response to make sure there's no error before adding message
        res = super().delete(request, *args, **kwargs)

        messages.add_message(
            request,
            messages.SUCCESS,
            format_html(
                _("Vous ne participez plus à l'événement <em>{}</em>"),
                self.object.event.name,
            ),
        )

        return res


class CalendarView(ObjectOpengraphMixin, DetailView):
    model = Calendar
    paginator_class = Paginator
    per_page = 10

    def get(self, request, *args, **kwargs):
        res = super().get(request, *args, **kwargs)
        if request.GET.get("iframe"):
            res.xframe_options_exempt = True
        return res

    def get_template_names(self):
        if self.request.GET.get("iframe"):
            return ["events/calendar_iframe.html"]
        return ["events/calendar.html"]

    def get_context_data(self, **kwargs):
        # get all ids of calendar that are either the one selected, or children of it
        calendar_ids = self.get_calendar_ids(self.object.id)

        all_events = (
            Event.objects.upcoming(as_of=timezone.now())
            .filter(calendar_items__calendar_id__in=calendar_ids)
            .order_by("start_time", "id")
            .distinct("start_time", "id")
        )
        paginator = self.paginator_class(all_events, self.per_page)

        page = self.request.GET.get("page")
        try:
            events = paginator.page(page)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)

        return super().get_context_data(
            events=events, default_event_image=settings.DEFAULT_EVENT_IMAGE
        )

    @staticmethod
    def get_calendar_ids(parent_id):
        ids = Calendar.objects.raw(
            """
        WITH RECURSIVE children AS (
            SELECT id
            FROM events_calendar
            WHERE id = %s
          UNION ALL
            SELECT c.id
            FROM events_calendar AS c
            JOIN children
            ON c.parent_id = children.id
        )
        SELECT id FROM children;
        """,
            [parent_id],
        )

        return list(ids)


class CalendarIcsView(DetailView):
    model = Calendar

    def render_to_response(self, context, **response_kwargs):
        calendar = ics.Calendar(
            events=[
                event.to_ics()
                for event in self.object.events.filter(
                    visibility=Event.VISIBILITY_PUBLIC
                )
            ]
        )

        return HttpResponse(calendar, content_type="text/calendar")


class ChangeEventLocationView(
    HardLoginRequiredMixin, PermissionsRequiredMixin, ChangeLocationBaseView
):
    template_name = "events/change_location.html"
    permissions_required = ("events.change_event",)
    form_class = EventGeocodingForm
    success_view_name = "manage_event"

    def get_queryset(self):
        return Event.objects.upcoming(as_of=timezone.now(), published_only=False)


class EditEventReportView(HardLoginRequiredMixin, PermissionsRequiredMixin, UpdateView):
    template_name = "events/edit_event_report.html"
    permissions_required = ("events.change_event",)
    form_class = EventReportForm

    def get_success_url(self):
        return reverse("manage_event", args=(self.object.pk,))

    def get_queryset(self):
        return Event.objects.past(as_of=timezone.now())


class UploadEventImageView(
    SoftLoginRequiredMixin, PermissionsRequiredMixin, CreateView
):
    template_name = "events/upload_event_image.html"
    form_class = UploadEventImageForm
    permissions_required = ("events.view_event",)
    permission_denied_to_not_found = True

    def get_queryset(self):
        return Event.objects.past(as_of=timezone.now())

    def get_success_url(self):
        return reverse("view_event", args=(self.event.pk,))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"author": self.request.user.person, "event": self.event})
        return kwargs

    def get_author_form(self):
        author_form_kwargs = {"instance": self.request.user.person}
        if self.request.method in ["POST", "PUT"]:
            author_form_kwargs["data"] = self.request.POST

        return AuthorForm(**author_form_kwargs)

    def get_context_data(self, **kwargs):
        if "author_form" not in kwargs:
            kwargs["author_form"] = self.get_author_form()

        return super().get_context_data(event=self.event, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None
        self.event = self.get_object()

        if not self.event.rsvps.filter(person=request.user.person).exists():
            raise PermissionDenied(
                _("Seuls les participants à l'événement peuvent poster des images")
            )

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        self.event = self.get_object()

        if not self.event.rsvps.filter(person=request.user.person).exists():
            raise PermissionDenied(
                _("Seuls les participants à l'événement peuvent poster des images")
            )

        form = self.get_form()
        author_form = self.get_author_form()

        if form.is_valid() and author_form.is_valid():
            return self.form_valid(form, author_form)
        else:
            return self.form_invalid(form, author_form)

    def form_invalid(self, form, author_form):
        return self.render_to_response(
            self.get_context_data(form=form, author_form=author_form)
        )

    def form_valid(self, form, author_form):
        author_form.save()
        form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            _("Votre photo a correctement été importée, merci de l'avoir partagée !"),
        )

        return HttpResponseRedirect(self.get_success_url())
