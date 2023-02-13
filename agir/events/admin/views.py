from itertools import groupby

from django.contrib import admin, messages
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import reverse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.views.generic.detail import SingleObjectMixin
from django_filters.views import FilterView
from unidecode import unidecode

from agir.events.admin.filters import EventFilterSet
from agir.events.admin.forms import NewParticipantForm
from agir.events.models import Event, EventSubtype, Calendar
from agir.lib.admin.panels import AdminViewMixin
from agir.people.person_forms.actions import get_people_form_class
from agir.people.person_forms.fields import is_actual_model_field
from .forms import AddOrganizerForm


def add_organizer(model_admin, request, pk):
    if not model_admin.has_change_permission(request) or not request.user.has_perm(
        "people.view_person"
    ):
        raise PermissionDenied

    event = model_admin.get_object(request, pk)

    if event is None:
        raise Http404(_("Pas d'événement avec cet identifiant."))

    if request.method == "POST":
        form = AddOrganizerForm(event, model_admin, data=request.POST)

        if form.is_valid():
            organizer_config = form.save()
            messages.success(
                request,
                _(
                    "{email} a bien été enregistré comme participant à l'événement"
                ).format(email=organizer_config.person.display_email),
            )

            return HttpResponseRedirect(
                reverse(
                    "%s:%s_%s_change"
                    % (
                        model_admin.admin_site.name,
                        event._meta.app_label,
                        event._meta.model_name,
                    ),
                    args=(event.pk,),
                )
            )
    else:
        form = AddOrganizerForm(event, model_admin)

    fieldsets = [(None, {"fields": ["person"]})]
    admin_form = admin.helpers.AdminForm(form, fieldsets, {})

    context = {
        "title": _("Ajouter un organisateur à l'événement: %s") % escape(event.name),
        "adminform": admin_form,
        "form": form,
        "is_popup": True,
        "opts": model_admin.model._meta,
        "original": event,
        "change": True,
        "add": False,
        "save_as": False,
        "show_save": True,
        "has_delete_permission": model_admin.has_delete_permission(request, event),
        "has_add_permission": model_admin.has_add_permission(request),
        "has_change_permission": model_admin.has_change_permission(request, event),
        "has_view_permission": model_admin.has_view_permission(request, event),
        "has_editable_inline_admin_formsets": False,
        "media": model_admin.media + admin_form.media,
    }
    context.update(model_admin.admin_site.each_context(request))

    request.current_app = model_admin.admin_site.name

    return TemplateResponse(request, "admin/events/add_organizer.html", context)


class EventSummaryView(AdminViewMixin, FilterView):
    filterset_class = EventFilterSet
    template_name = "admin/events/event_summary.html"

    def get_filterset_kwargs(self, filterset_class):
        return {
            "data": self.request.POST or None,
            "request": self.request,
            "queryset": self.get_queryset(),
        }

    def get_queryset(self):
        return Event.objects.all()

    def get_grouped_events(self):
        if self.object_list:
            events = sorted(
                self.object_list,
                key=lambda e: (unidecode(e.region), e.start_time, e.end_time),
            )
            tz = timezone.get_current_timezone()

            events_by_region = groupby(events, key=lambda e: e.region)
            res = []
            for region, events in events_by_region:
                events_by_date = groupby(
                    events, key=lambda e: e.start_time.astimezone(tz).date()
                )

                res.append(
                    (region, [(date, list(events)) for date, events in events_by_date])
                )

            return res

    def get_context_data(self, *, object_list=None, **kwargs):
        calendars_field = self.filterset.form.fields["calendars"]
        subtype_field = self.filterset.form.fields["subtype"]

        calendars_field.widget = AutocompleteSelectMultiple(
            Calendar._meta.get_field("events"), self.kwargs["model_admin"].admin_site
        )
        subtype_field.widget = AutocompleteSelectMultiple(
            EventSubtype._meta.get_field("events"),
            self.kwargs["model_admin"].admin_site,
        )

        calendars_field.queryset = Calendar.objects.all()
        subtype_field.queryset = EventSubtype.objects.exclude(
            visibility=EventSubtype.VISIBILITY_NONE
        )

        return super().get_context_data(
            title="Résumé des événements",
            opts=self.kwargs["model_admin"].model._meta,
            add=False,
            change=False,
            is_popup=False,
            save_as=False,
            has_add_permission=False,
            has_change_permission=False,
            has_view_permission=False,
            has_editable_inline_admin_formsets=False,
            has_delete_permission=False,
            show_close=False,
            events_by_region=self.get_grouped_events(),
            **self.get_admin_helpers(self.filterset.form, self.filterset.base_filters),
            **kwargs
        )

    def get(self, request, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)

        self.object_list = None

        context = self.get_context_data(filter=self.filterset)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)

        if self.filterset.is_valid() or not self.get_strict():
            self.object_list = self.filterset.qs
        else:
            self.object_list = None

        context = self.get_context_data(filter=self.filterset)
        return self.render_to_response(context)


class AddParticipantView(SingleObjectMixin, FormView):
    model_admin = None
    queryset = Event.objects.filter(subscription_form__isnull=False)
    template_name = "admin/events/add_participant.html"

    def get(self, request, *args, **kwargs):
        self.object = self.event = self.get_object()
        if not self.event.subscription_form:
            raise Http404()

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.event = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form_class(self):
        person_form = self.event.subscription_form

        return get_people_form_class(
            person_form,
            base_form=NewParticipantForm,
            include_inherited_model_fields=True,
        )

    @cached_property
    def additional_billing_fields(self):
        form_person_fields = {
            f
            for f, descriptor in self.event.subscription_form.fields_dict.items()
            if is_actual_model_field(descriptor)
        }

        return [
            f for f in NewParticipantForm._meta.fields if f not in form_person_fields
        ] + ["payment_mode"]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.event.is_free:
            for field in self.additional_billing_fields:
                form.fields.pop(field)
        else:
            for field in self.additional_billing_fields:
                form.fields[field].required = False

        return form

    def get_form_kwargs(self):
        return {
            "model_admin": self.model_admin,
            "event": self.event,
            **super().get_form_kwargs(),
        }

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data()
        form = kwargs["form"]

        fieldsets = form.fieldsets

        if not self.event.is_free:
            fieldsets = fieldsets + [
                ("Facturation", {"fields": self.additional_billing_fields})
            ]

        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        kwargs.update(
            {
                "title": _("Ajouter un participant à l'événement: %s")
                % escape(self.event.name),
                "adminform": admin_form,
                "form": form,
                "is_popup": True,
                "opts": self.model_admin.model._meta,
                "original": self.event,
                "change": True,
                "add": False,
                "save_as": False,
                "show_save": True,
                "has_delete_permission": self.model_admin.has_delete_permission(
                    self.request, self.event
                ),
                "has_add_permission": self.model_admin.has_add_permission(self.request),
                "has_change_permission": self.model_admin.has_change_permission(
                    self.request, self.event
                ),
                "has_view_permission": self.model_admin.has_view_permission(
                    self.request, self.event
                ),
                "has_editable_inline_admin_formsets": False,
                "media": self.model_admin.media + admin_form.media,
            }
        )

        return kwargs

    def form_valid(self, form):
        form.save()

        if (
            self.event.is_free
            or self.event.get_price(form.submission and form.submission.data) == 0
        ):
            form.free_rsvp()
            self.model_admin.message_user(
                self.request,
                "La personne a bien été inscrite à l'événement.",
                messages.SUCCESS,
            )
            return HttpResponseRedirect(self.request.path)

        return form.redirect_to_payment()
