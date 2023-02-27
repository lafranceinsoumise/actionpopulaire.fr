from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import Q
from django.urls import path
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from agir.event_requests.models import EventAsset, EventSpeaker
from agir.events import models
from agir.events.models import Calendar, RSVP
from agir.events.models import GroupAttendee
from agir.groups.models import SupportGroup, Membership
from agir.lib.admin.filters import (
    CountryListFilter,
    DepartementListFilter,
    RegionListFilter,
    CirconscriptionLegislativeFilter,
)
from agir.lib.admin.panels import CenterOnFranceMixin
from agir.lib.utils import front_url, replace_datetime_timezone
from agir.people.admin.views import FormSubmissionViewsMixin
from agir.people.models import PersonFormSubmission
from agir.people.person_forms.display import PersonFormDisplay
from . import actions
from . import views
from .filters import RelatedEventFilter
from .forms import EventAdminForm, EventSubtypeAdminForm
from ...event_requests.admin.inlines import EventAssetInline


class EventStatusFilter(admin.SimpleListFilter):
    title = _("Statut")

    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("finished", _("Terminé")),
            ("current", _("En cours")),
            ("upcoming", _("À venir")),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "finished":
            return queryset.filter(end_time__lt=now)
        elif self.value() == "current":
            return queryset.filter(start_time__lte=now, end_time__gte=now)
        elif self.value() == "upcoming":
            return queryset.filter(start_time__gt=now)
        else:
            return queryset


class EventHasReportFilter(admin.SimpleListFilter):
    title = _("Compte-rendu présent")

    parameter_name = "has_report"

    def lookups(self, request, model_admin):
        return (("yes", _("Présent")), ("no", _("Absent")))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(report_content="")
        if self.value() == "no":
            return queryset.filter(report_content="")
        return queryset


class EventCalendarFilter(admin.SimpleListFilter):
    title = "Calendrier"
    parameter_name = "calendar"

    def lookups(self, request, model_admin):
        return ((c.pk, c.name) for c in Calendar.objects.filter(archived=False))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(calendars__pk=self.value())
        return queryset


class OrganizerConfigInlineAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance._state.adding:
            self.fields["as_group"].queryset = SupportGroup.objects.none()
        else:
            self.fields["as_group"].queryset = SupportGroup.objects.filter(
                memberships__person=self.instance.person,
                memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
            )


class OrganizerConfigInline(admin.TabularInline):
    verbose_name = "Organisateur·ice de l'événement"
    verbose_name_plural = "Organisateur·ices de l'événement"
    model = models.OrganizerConfig
    fields = ("person_link", "as_group")
    readonly_fields = ("person_link",)
    extra = 0
    form = OrganizerConfigInlineAdminForm

    @admin.display(description="Personne")
    def person_link(self, obj):
        return mark_safe(
            format_html(
                '<a href="{}">{}</a>',
                reverse("admin:people_person_change", args=(obj.person.id,)),
                escape(obj.person.display_email),
            )
        )

    def has_add_permission(self, request, obj=None):
        return False


class EventImageInline(admin.TabularInline):
    verbose_name = "Image de l'événement"
    verbose_name_plural = "Images de l'événement"
    model = models.EventImage
    fields = ("image_link", "author_link", "legend")
    readonly_fields = ("image_link", "author_link")
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Image")
    def image_link(self, obj):
        return mark_safe(
            format_html(
                '<a href="{}"><img src="{}"></a>',
                obj.image.url,
                obj.image.admin_thumbnail.url,
            )
        )

    @admin.display(description="Auteur·ice")
    def author_link(self, obj):
        return mark_safe(
            format_html(
                '<a href="{}">{}</a>',
                reverse("admin:people_person_change", args=(obj.author.id,)),
                escape(obj.author.display_email),
            )
        )


class EventRsvpPersonFormDisplay(PersonFormDisplay):
    def get_submission_rsvp_or_guest(self, submission):
        try:
            return submission.rsvp
        except PersonFormSubmission.rsvp.RelatedObjectDoesNotExist:
            return submission.rsvp_guest

    def get_admin_fields_label(self, form, *args, **kwargs):
        fields = super().get_admin_fields_label(form, *args, **kwargs)

        if not form.event.is_free:
            fields.append("Paiement")

        if form.event.allow_guests:
            fields.append("Invité⋅e par")

        return fields

    def _get_admin_fields(self, submissions, html=True):
        results = super()._get_admin_fields(submissions, html)
        event = submissions[0].form.event

        if not event.is_free:
            for s, r in zip(submissions, results):
                r.append(
                    format_html(
                        '{} <a href="{}" target="_blank"title="Voir le détail">&#128269;</a>',
                        self.get_submission_rsvp_or_guest(s).get_status_display(),
                        settings.API_DOMAIN
                        + reverse(
                            "admin:payments_payment_change",
                            args=(self.get_submission_rsvp_or_guest(s).payment_id,),
                        ),
                    )
                    if html
                    and self.get_submission_rsvp_or_guest(s).payment_id is not None
                    else self.get_submission_rsvp_or_guest(s).get_status_display()
                )

        if event.allow_guests:
            for s, r in zip(submissions, results):
                try:
                    r.append(
                        format_html(
                            '<a href="{}" target="_blank">{}</a>',
                            settings.API_DOMAIN
                            + reverse(
                                "admin:people_person_change",
                                args=(s.rsvp_guest.rsvp.person.pk,),
                            ),
                            s.rsvp_guest.rsvp.person,
                        )
                        if html
                        else s.rsvp_guest.rsvp.person
                    )
                except PersonFormSubmission.rsvp_guest.RelatedObjectDoesNotExist:
                    r.append("")

        return results


class AutoCompleteEventView(AutocompleteJsonView):
    def get_queryset(self):
        """Return queryset based on ModelAdmin.get_search_results()."""
        return models.Event.objects.simple_search(self.term)


@admin.register(models.Event)
class EventAdmin(FormSubmissionViewsMixin, CenterOnFranceMixin, OSMGeoAdmin):
    form = EventAdminForm
    person_form_display = EventRsvpPersonFormDisplay()
    show_full_result_count = False

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "name",
                    "link",
                    "created",
                    "modified",
                    "add_organizer_button",
                )
            },
        ),
        (
            _("Informations"),
            {
                "fields": (
                    "subtype",
                    "description",
                    "allow_html",
                    "image",
                    "start_time",
                    "end_time",
                    "timezone",
                    "calendars",
                    "tags",
                    "visibility",
                    "do_not_list",
                    "send_visibility_notification",
                    "facebook",
                    "meta",
                    "suggestion_segment",
                    "attendant_notice",
                )
            },
        ),
        (
            _("Inscription"),
            {
                "fields": (
                    "max_participants",
                    "allow_guests",
                    "subscription_form",
                    "participants_display",
                    "group_participants_display",
                    "rsvps_buttons",
                    "payment_parameters",
                    "enable_jitsi",
                    "participation_template",
                )
            },
        ),
        (
            _("Lieu"),
            {
                "fields": (
                    "online_url",
                    "location_name",
                    "location_address1",
                    "location_address2",
                    "location_city",
                    "location_zip",
                    "location_departement_id",
                    "location_state",
                    "location_country",
                    "coordinates",
                    "coordinates_type",
                    "redo_geocoding",
                )
            },
        ),
        (
            _("Contact"),
            {
                "fields": (
                    "contact_name",
                    "contact_email",
                    "contact_phone",
                    "contact_hide_phone",
                )
            },
        ),
        (
            _("Compte-rendu"),
            {"fields": ("report_content", "report_image", "report_summary_sent")},
        ),
        (
            _("Intervenant"),
            {"fields": ("event_speaker",)},
        ),
    )

    inlines = (OrganizerConfigInline, EventImageInline, EventAssetInline)

    readonly_fields = (
        "id",
        "link",
        "add_organizer_button",
        "organizers",
        "created",
        "modified",
        "location_departement_id",
        "coordinates_type",
        "rsvps_buttons",
        "participants_display",
        "group_participants_display",
    )
    date_hierarchy = "start_time"

    list_display = (
        "name",
        "visibility",
        "calendar_names",
        "location_short",
        "start_time",
        "created",
    )
    list_filter = (
        EventStatusFilter,
        "visibility",
        EventHasReportFilter,
        CountryListFilter,
        CirconscriptionLegislativeFilter,
        DepartementListFilter,
        RegionListFilter,
        "coordinates_type",
        "subtype__type",
        "subtype",
        EventCalendarFilter,
        "tags",
    )

    search_fields = ("name",)

    actions = (
        actions.export_events,
        actions.make_published,
        actions.make_private,
        actions.unpublish,
    )

    autocomplete_fields = (
        "tags",
        "subscription_form",
        "suggestion_segment",
        "event_speaker",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("calendars")

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.search(search_term)

        use_distinct = False

        return queryset, use_distinct

    def location_short(self, object):
        return _("{zip} {city}, {country}").format(
            zip=object.location_zip,
            city=object.location_city,
            country=object.location_country.name,
        )

    location_short.short_description = _("Lieu")
    location_short.admin_order_field = "location_city"

    def calendar_names(self, object):
        return ", ".join(c.name for c in object.calendars.all())

    calendar_names.short_description = _("Agendas")

    def add_organizer_button(self, object):
        if object.pk is None:
            return mark_safe("-")
        return (
            format_html(
                '<a href="{}" class="button">+ Organisateur</a>',
                reverse("admin:events_event_add_organizer", args=[object.pk]),
            )
            if object.pk
            else "-"
        )

    add_organizer_button.short_description = _("Ajouter un organisateur")

    def attendee_count(self, object):
        if object.is_free:
            return str(object.all_attendee_count)

        return _(
            f"{object.all_attendee_count} (dont {object.confirmed_attendee_count} confirmés)"
        )

    attendee_count.short_description = _("Nombre de personnes inscrites")
    attendee_count.admin_order_field = "all_attendee_count"

    def link(self, object):
        if object.pk:
            return format_html(
                '<a href="{0}">{0}</a>',
                front_url("view_event", kwargs={"pk": object.pk}),
            )
        else:
            return "-"

    link.short_description = _("Page sur le site")

    def rsvps_buttons(self, object):
        if object.subscription_form is None or object.pk is None:
            return mark_safe("-")
        else:
            return format_html(
                '<a href="{view_results_link}" class="button">Voir les inscriptions</a><br>'
                '<a href="{download_results_link}" class="button">Télécharger les inscriptions</a><br>'
                '<a href="{add_participant_link}" class="button">Inscrire quelq\'un</a>',
                view_results_link=reverse(
                    "admin:events_event_rsvps_view_results", args=(object.pk,)
                ),
                download_results_link=reverse(
                    "admin:events_event_rsvps_download_results", args=(object.pk,)
                ),
                add_participant_link=reverse(
                    "admin:events_event_add_participant", args=(object.pk,)
                ),
            )

    rsvps_buttons.short_description = _("Inscriptions")

    def participants_display(self, obj):
        if obj:
            label = str(obj.participants)

            if obj.participants != obj.participants_confirmes:
                label = f"{obj.participants} participants (dont {obj.participants_confirmes} confirmés)"

            return mark_safe(f"{label}&emsp;{self.event_rsvp_changelist_link(obj)}")
        return "-"

    participants_display.short_description = "Nombre de participants"

    def group_participants_display(self, obj):
        if obj.groups_attendees.exists():
            return mark_safe(
                f"{obj.groups_attendees.count()}&emsp;{self.event_group_attendees_changelist_link(obj)}"
            )
        return "-"

    group_participants_display.short_description = "Nombre de groupes participants"

    def add_organizer(self, request, pk):
        return views.add_organizer(self, request, pk)

    def get_submission_queryset(self, form):
        return (
            PersonFormSubmission.objects.filter(
                Q(rsvp__event=self.instance) | Q(guest_rsvp__event=self.instance),
            )
            .exclude(rsvp__status=RSVP.STATUS_CANCELED)
            .select_related("rsvp", "rsvp_guest")
        )

    # noinspection PyMethodOverriding
    def view_results(self, request, pk):
        self.instance = models.Event.objects.get(pk=pk)
        return super().view_results(
            request,
            self.instance.subscription_form.id,
            title="Inscriptions à l'événement %s" % self.instance.name,
        )

    def download_results(self, request, pk):
        self.instance = models.Event.objects.get(pk=pk)
        return super().download_results(request, self.instance.subscription_form.id)

    def export_summary(self, request):
        return views.EventSummaryView.as_view()(request, model_admin=self)

    def autocomplete_view(self, request):
        return AutoCompleteEventView.as_view(model_admin=self)(request)

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/add_organizer/",
                self.admin_site.admin_view(self.add_organizer),
                name="events_event_add_organizer",
            ),
            path(
                "<uuid:pk>/add_participant/",
                self.admin_site.admin_view(
                    views.AddParticipantView.as_view(model_admin=self)
                ),
                name="events_event_add_participant",
            ),
            path(
                "<uuid:pk>/view_rsvps/",
                self.admin_site.admin_view(self.view_results),
                name="events_event_rsvps_view_results",
            ),
            path(
                "<uuid:pk>/download_rsvps/",
                self.admin_site.admin_view(self.download_results),
                name="events_event_rsvps_download_results",
            ),
            path(
                "resume/",
                self.admin_site.admin_view(self.export_summary),
                name="events_event_export_summary",
            ),
        ] + super().get_urls()

    def event_rsvp_changelist_link(self, obj):
        return format_html(
            '<a class="button" style="color: white;" href="{link}?event={event_id}">Voir les participants</a>',
            link=reverse("admin:events_rsvp_changelist"),
            event_id=str(obj.id),
        )

    event_rsvp_changelist_link.short_description = ""

    def event_group_attendees_changelist_link(self, obj):
        return format_html(
            '<a class="button" style="color: white;" href="{link}?event={event_id}">Voir les groupes</a>',
            link=reverse("admin:events_groupattendee_changelist"),
            event_id=str(obj.id),
        )

    def get_list_display(self, request):
        if request.user.has_perm("events.view_rsvp"):
            return self.list_display + ("event_rsvp_changelist_link",)
        return self.list_display

    class Media:
        # classe Media requise par le CirconscriptionLegislativeFilter, quand bien même elle est vide
        pass

    def render_change_form(self, *args, obj=None, **kwargs):
        # Display the event start and end date relative to the event timezone
        if obj:
            timezone.activate(obj.timezone)
        return super().render_change_form(*args, obj=obj, **kwargs)

    def save_model(self, request, obj, form, change):
        # Update the event start and end date relative to the event timezone
        if "timezone" in form.changed_data or "start_time" in form.changed_data:
            obj.start_time = replace_datetime_timezone(obj.start_time, obj.timezone)
        if "timezone" in form.changed_data or "end_time" in form.changed_data:
            obj.end_time = replace_datetime_timezone(obj.end_time, obj.timezone)
        return super().save_model(request, obj, form, change)

    def save_form(self, request, form, change):
        return form.save(commit=False, request=request)


@admin.register(models.Calendar)
class CalendarAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "slug",
        "link",
        "parent",
        "user_contributed",
        "description",
        "image",
        "archived",
    )
    list_display = ("name", "slug", "user_contributed", "parent", "archived")
    readonly_fields = ("link",)
    search_fields = ("name", "parent__name")

    def link(self, object):
        if object.slug:
            return format_html(
                '<a href="{0}">{0}</a>',
                front_url("view_calendar", kwargs={"slug": object.slug}),
            )
        else:
            return "-"

    link.short_description = _("Lien vers l'agenda")


@admin.register(models.EventTag)
class EventTagAdmin(admin.ModelAdmin):
    search_fields = ("label",)
    pass


@admin.register(models.EventSubtype)
class EventSubtypeAdmin(admin.ModelAdmin):
    form = EventSubtypeAdminForm
    list_display = (
        "label",
        "description",
        "type",
        "visibility",
        "has_priority",
        "related_project_type",
    )
    list_filter = ("type", "visibility", "has_priority", "related_project_type")

    search_fields = ("label", "description")
    autocomplete_fields = ("report_person_form",)


@admin.register(models.JitsiMeeting)
class JitsiMeetingAdmin(admin.ModelAdmin):
    autocomplete_fields = ("event",)
    readonly_fields = ("start_time", "end_time", "display_link")
    list_display = ("room_name", "event", "start_time", "end_time", "members")

    def members(self, object):
        return object.rsvps.count()

    def display_link(self, object):
        return format_html('<a target="_blank" href="{0}">{0}</a>', object.link)


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "person_link",
        "event_link",
        "status",
        "guest_count",
    )

    search_fields = ("person__search", "event__name")
    list_filter = (RelatedEventFilter, "status")
    list_display_links = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm("events.delete_rsvp")

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("events.view_rsvp")

    def get_list_display(self, request):
        if not request.user.has_perm("events.view_event"):
            return self.list_display

        if request.GET.get("event") is not None:
            return tuple(f for f in self.list_display if f != "event_link")

        return (*self.list_display, "filter_by_event_button")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("event", "person")
            .prefetch_related("identified_guests")
        )

    def person_link(self, obj):
        return format_html(
            '<a href="{link}">{person}</a>',
            person=str(obj.person),
            link=reverse("admin:people_person_change", args=[obj.person.pk]),
        )

    person_link.short_description = "Personne"

    def person_contact_phone(self, obj):
        return obj.person.contact_phone

    person_contact_phone.short_description = "Numéro de téléphone"

    def event_link(self, obj):
        return format_html(
            '<a href="{link}">{event}</a>',
            event=str(obj.event),
            link=reverse("admin:events_event_change", args=[obj.id]),
        )

    event_link.short_description = "Événement"

    def filter_by_event_button(self, obj):
        return format_html(
            '<a class="button default" style="color: white;" href="{link}?event={event_id}">Voir uniquement cet événement</a>',
            link=reverse("admin:events_rsvp_changelist"),
            event_id=str(obj.event_id),
        )

    filter_by_event_button.short_description = ""

    def guest_count(self, obj):
        return obj.guests

    guest_count.short_description = "Invités"

    class Media:
        pass


@admin.register(GroupAttendee)
class GroupAttendeeAdmin(admin.ModelAdmin):
    list_display = (
        "organizer",
        "group",
        "event",
    )
    search_fields = ("organizer__search", "event__name", "group__name")
    list_display_links = None

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm("events.delete_rsvp")

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("events.view_rsvp")

    def get_list_display(self, request):
        if not request.user.has_perm("events.view_event"):
            return self.list_display

        return self.list_display + ("filter_by_event_button",)

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related("event", "organizer", "group")
        )

    def person_link(self, obj):
        return format_html(
            '<a href="{link}">{person}</a>',
            person=str(obj.person),
            link=reverse("admin:people_person_change", args=[obj.id]),
        )

    person_link.short_description = "Personne"

    def event_link(self, obj):
        return format_html(
            '<a href="{link}">{event}</a>',
            event=str(obj.event),
            link=reverse("admin:events_event_change", args=[obj.id]),
        )

    event_link.short_description = "Événement"

    def filter_by_event_button(self, obj):
        return format_html(
            '<a class="button default" style="color: white;" href="{link}?event={event_id}">Voir uniquement cet événement</a>',
            link=reverse("admin:events_groupattendee_changelist"),
            event_id=str(obj.event_id),
        )

    filter_by_event_button.short_description = ""

    def guest_count(self, obj):
        return obj.guests

    guest_count.short_description = "Invités"

    class Media:
        pass
