from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.humanize.templatetags import humanize
from django.db.models import Q
from django.urls import path
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, escape, format_html_join
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _, ngettext

from agir.events import models
from agir.events.models import Calendar, RSVP, IdentifiedGuest
from agir.events.models import GroupAttendee
from agir.groups.models import SupportGroup, Membership
from agir.lib.admin.filters import (
    CountryListFilter,
    DepartementListFilter,
    RegionListFilter,
    CirconscriptionLegislativeFilter,
    ParticipantFilter,
)
from agir.lib.admin.panels import CenterOnFranceMixin
from agir.lib.utils import front_url, replace_datetime_timezone
from agir.people.admin.views import FormSubmissionViewsMixin
from agir.people.models import PersonFormSubmission
from agir.people.person_forms.display import PersonFormDisplay
from . import actions
from . import views
from .filters import (
    OrganizerGroupFilter,
    GroupAttendeeFilter,
    EventSubtypeFilter,
    RelatedEventFilter,
    RSVPGuestFilter,
)
from .forms import EventAdminForm, EventSubtypeAdminForm
from .views import reset_feuille_externe
from ..serializers import EventEmailCampaignSerializer
from ...event_requests.admin.inlines import EventAssetInline
from ...lib.admin.utils import (
    display_link,
    display_list_of_links,
    display_json_details,
    admin_url,
)


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
    def __init__(self, event=None):
        self.event = event
        super().__init__()

    def get_submission_rsvp_or_guest(self, submission):
        try:
            return submission.rsvp
        except PersonFormSubmission.rsvp.RelatedObjectDoesNotExist:
            return submission.rsvp_guest

    def get_admin_fields_label(self, form, *args, **kwargs):
        fields = super().get_admin_fields_label(form, *args, **kwargs)

        if not self.event.is_free:
            fields.append("Paiement")

        if self.event.allow_guests:
            fields.append("Invité⋅e par")

        return fields

    def _get_admin_fields(self, submissions, html=True):
        results = super()._get_admin_fields(submissions, html)

        if not self.event.is_free:
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

        if self.event.allow_guests:
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
                    "lien_feuille_externe",
                    "participants_display",
                    "unavailable_display",
                    "group_participants_display",
                    "rsvps_buttons",
                    "payment_parameters",
                    "volunteer_application_form",
                    "volunteer_application_form_submissions",
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
            _("Intervenant·es"),
            {"fields": ("event_speakers",)},
        ),
        (
            _("Mailing"),
            {
                "fields": (
                    "campaign_template",
                    "email_campaign",
                    "email_campaign_modified",
                    "mailing_actions",
                    "email_data_preview",
                )
            },
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
        "unavailable_display",
        "group_participants_display",
        "campaign_template",
        "mailing_actions",
        "email_campaign_modified",
        "email_data_preview",
        "volunteer_application_form_submissions",
    )
    date_hierarchy = "start_time"

    list_display = (
        "name",
        "visibility",
        "calendar_names",
        "location_short",
        "start_time",
        "created",
        "acceptable_for_group_certification",
    )
    list_filter = (
        EventStatusFilter,
        "visibility",
        OrganizerGroupFilter,
        ParticipantFilter,
        GroupAttendeeFilter,
        EventHasReportFilter,
        "subtype__type",
        EventSubtypeFilter,
        "subtype__is_acceptable_for_group_certification",
        EventCalendarFilter,
        DepartementListFilter,
        CirconscriptionLegislativeFilter,
        RegionListFilter,
        CountryListFilter,
        "coordinates_type",
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
        "volunteer_application_form",
        "suggestion_segment",
        "event_speakers",
        "email_campaign",
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

    @admin.display(description="Certification", boolean=True)
    def acceptable_for_group_certification(self, obj):
        return obj and obj.subtype.is_acceptable_for_group_certification

    @admin.display(description="Calendriers")
    def calendar_names(self, object):
        return ", ".join(c.name for c in object.calendars.all())

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
        if not object.pk:
            return "-"

        links = []

        if object.subscription_form:
            links.extend(
                [
                    ("admin:events_event_rsvps_view_results", "Voir les inscriptions"),
                    (
                        "admin:events_event_rsvps_download_results",
                        "Télécharger les inscriptions",
                    ),
                    ("admin:events_event_add_participant", "Inscrire quelqu'un"),
                ]
            )

        if object.lien_feuille_externe:
            links.append(
                (
                    "admin:events_event_reset_feuille_externe",
                    "Réinitialiser la feuille externe",
                )
            )

        return format_html(
            '<div style="display: flex; gap: 10px;">{}</div>',
            format_html_join(
                "",
                '<a href="{}" class="button">{}</a>',
                ((reverse(view, args=(object.pk,)), label) for view, label in links),
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

    def unavailable_display(self, obj):
        if not obj:
            return "-"

        unavailable_count = obj.annotated_attendees.filter(unavailable=True).count()

        if unavailable_count == 0:
            return "-"

        return ngettext(
            "1 personne", f"{unavailable_count} personnes", unavailable_count
        )

        return "-"

    unavailable_display.short_description = "Nombre de personnes indisponibles"

    def group_participants_display(self, obj):
        if obj.groups_attendees.exists():
            return mark_safe(
                f"{obj.groups_attendees.count()}&emsp;{self.event_group_attendees_changelist_link(obj)}"
            )
        return "-"

    group_participants_display.short_description = "Nombre de groupes participants"

    @admin.display(description="Réponses au formulaire d'appel à volontaires")
    def volunteer_application_form_submissions(self, obj):
        if not obj or not obj.volunteer_application_form:
            return "-"

        count = (
            obj.volunteer_application_form.submissions.values("person_id")
            .distinct()
            .count()
        )

        if count == 0:
            return "Aucune réponse n'a encore été reçue "

        count = ngettext("Voir la réponse", f"Voir les {count} réponses", count)

        link = admin_url(
            "people_personform_view_results", args=(obj.volunteer_application_form.pk,)
        )

        return display_link(link, count)

    def add_organizer(self, request, pk):
        return views.add_organizer(self, request, pk)

    def get_submission_queryset(self, form):
        return (
            PersonFormSubmission.objects.filter(
                Q(rsvp__event=self.instance) | Q(guest_rsvp__event=self.instance),
            )
            .exclude(rsvp__status=RSVP.Status.CANCELLED)
            .select_related("rsvp", "rsvp_guest")
        )

    # noinspection PyMethodOverriding
    def view_results(self, request, pk):
        self.instance = models.Event.objects.get(pk=pk)
        self.person_form_display = EventRsvpPersonFormDisplay(event=self.instance)
        return super().view_results(
            request,
            self.instance.subscription_form.id,
            title="Inscriptions à l'événement %s" % self.instance.name,
            download_url=admin_url(
                "admin:events_event_rsvps_download_results", args=(self.instance.pk,)
            ),
        )

    def download_results(self, request, pk):
        self.instance = models.Event.objects.get(pk=pk)
        self.person_form_display = EventRsvpPersonFormDisplay(event=self.instance)
        return super().download_results(
            request,
            self.instance.subscription_form.id,
            filename=slugify(self.instance.name),
        )

    def export_summary(self, request):
        return views.EventSummaryView.as_view()(request, model_admin=self)

    def autocomplete_view(self, request):
        return AutoCompleteEventView.as_view(model_admin=self)(request)

    def reset_feuille_externe(self, request, pk):
        return reset_feuille_externe(self, request, pk)

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
            path(
                "<uuid:pk>/generate-mailing-campaign/",
                self.admin_site.admin_view(self.generate_mailing_campaign),
                name="events_event_generate_mailing_campaign",
            ),
            path(
                "<uuid:pk>/reset_feuille_externe/",
                self.admin_site.admin_view(self.reset_feuille_externe),
                name="events_event_reset_feuille_externe",
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

    def save_model(self, request, obj, form, change):
        # Update the event start and end date relative to the event timezone
        if "timezone" in form.changed_data or "start_time" in form.changed_data:
            obj.start_time = replace_datetime_timezone(obj.start_time, obj.timezone)
        if "timezone" in form.changed_data or "end_time" in form.changed_data:
            obj.end_time = replace_datetime_timezone(obj.end_time, obj.timezone)
        return super().save_model(request, obj, form, change)

    def save_form(self, request, form, change):
        return form.save(commit=False, request=request)

    @admin.display(description="Modèle de campagne")
    def campaign_template(self, obj):
        if not obj:
            return "-"

        return display_link(
            obj.subtype.campaign_template,
            empty_text="Aucun modèle de campagne e-mail n'a été défini pour ce sous-type d'événement",
        )

    @admin.display(description="Dernière modification")
    def email_campaign_modified(self, obj):
        if not obj or not obj.email_campaign:
            return "-"

        return humanize.naturaltime(obj.email_campaign.updated)

    def generate_mailing_campaign(self, request, pk):
        return views.generate_mailing_campaign(self, request, pk)

    @admin.display(description="Données")
    def email_data_preview(self, obj):
        if not obj or not obj.subtype.campaign_template:
            return "-"

        return format_html(
            "<details>"
            "<summary style='cursor:pointer;'>Variables et valeurs par défaut</summary>"
            "<p style='font-size:11px;color:var(--body-quiet-color);'>"
            "Les variables commençant par le préfixe <code>campaign_</code> seront utilisées comme paramètres de la "
            "campagne.<br/>Les autres pourront être utilisées pour la personnalisation du corps du message à envoyer, "
            "lorsque le modèle utilisé le prévoit."
            "</p>"
            "<p><dl>{}</dl></p>"
            "</details>",
            format_html_join(
                "",
                "<dt style='display:inline;margin:.2em 0;'><code style='padding:.4em;background:#FCF7E3;'>[{}]</code></dt>"
                "&ensp;"
                "<dd style='display:inline;margin:.2em 0;'><code>{}</code></dd>"
                "<div style='height:.5em'></div>",
                [
                    (key, value)
                    for key, value in EventEmailCampaignSerializer(obj).data.items()
                ],
            ),
        )

    @admin.display(description="Actions")
    def mailing_actions(self, obj):
        if not obj or not obj.pk or not obj.subtype.campaign_template:
            return "-"

        if obj.email_campaign:
            return display_list_of_links(
                (
                    (obj.email_campaign, "Voir la campagne"),
                    (
                        reverse(
                            "admin:nuntius_campaign_mosaico_preview",
                            args=[obj.email_campaign.pk],
                        ),
                        "Aperçu du message",
                    ),
                    (
                        reverse(
                            "admin:events_event_generate_mailing_campaign",
                            args=[obj.pk],
                        ),
                        "Réinitialiser la campagne",
                    ),
                ),
                button=True,
            ) + mark_safe(
                "<p class='help' style='margin: 10px 0 0; padding: 0;'>"
                "⚠&nbsp;En cliquant sur « Réinitialiser la campagne » les données "
                "existantes de la campagne seront écrasées."
                "</p>"
            )

        return display_link(
            reverse(
                "admin:events_event_generate_mailing_campaign",
                args=[obj.pk],
            ),
            "Créer une campagne à partir du modèle",
            button=True,
        )


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
    save_on_top = True
    form = EventSubtypeAdminForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "label",
                    "type",
                    "description",
                    "hide_text_label",
                    "has_priority",
                )
            },
        ),
        (
            "Liens",
            {
                "fields": (
                    "event_list_link",
                    "map_link",
                    "calendar_link",
                )
            },
        ),
        (
            "Autorisations",
            {
                "fields": (
                    "visibility",
                    "for_supportgroup_type",
                    "for_supportgroups",
                    "is_coorganizable",
                    "for_organizer_group_members_only",
                    "unauthorized_message",
                    "is_editable",
                    "is_acceptable_for_group_certification",
                    "allow_external",
                    "external_help_text",
                    "config",
                )
            },
        ),
        (
            "Icône",
            {
                "fields": (
                    "icon_name",
                    "color",
                    "icon_preview",
                    "emoji",
                    "icon_anchor_x",
                    "icon_anchor_y",
                    "popup_anchor_y",
                )
            },
        ),
        (
            "Valeurs par défaut",
            {
                "fields": (
                    "default_description",
                    "default_image",
                    "default_image_preview",
                    "campaign_template",
                )
            },
        ),
        (
            "Bilan",
            {"fields": ("report_person_form",)},
        ),
        (
            "Gestion",
            {
                "fields": (
                    "related_project_type",
                    "required_documents",
                )
            },
        ),
    )
    list_display = (
        "label",
        "description",
        "emoji",
        "type",
        "visibility",
        "for_group_type",
        "for_groups",
        "priority",
        "certification",
        "private",
        "coorganization_allowed",
    )
    list_filter = (
        "type",
        "visibility",
        "has_priority",
        "is_acceptable_for_group_certification",
        "for_organizer_group_members_only",
        "is_coorganizable",
        "related_project_type",
    )
    search_fields = ("label", "description")
    autocomplete_fields = (
        "report_person_form",
        "campaign_template",
        "for_supportgroups",
    )
    readonly_fields = (
        "event_list_link",
        "map_link",
        "calendar_link",
        "default_image_preview",
        "icon_preview",
    )

    @admin.display(description="Événements")
    def event_list_link(self, obj):
        if not obj or not obj.pk:
            return "-"

        count = obj.events.count()

        if count == 0:
            return "Aucun événement de ce type n'a pas encore été créé"

        url = admin_url("events_event_changelist", query={"subtype_id": obj.id})
        text = ngettext(
            "Voir l'événement de ce type",
            f"Voir les {humanize.apnumber(count)} événements de ce type",
            count,
        )

        return format_html(
            f'<a class="button" href="{url}">{text}</a>',
        )

    @admin.display(description="Cartes")
    def map_link(self, obj):
        if not obj or not obj.pk:
            return "-"

        url = front_url(
            "carte:events_map",
            absolute=True,
            query={"subtype": obj.label},
        )
        return format_html(
            f'<a target="_blank" href="{url}">🔮&ensp;Événements à venir</a>'
            f"&emsp;·&emsp;"
            f'<a target="_blank" href="{url}&include_past=1">📜&ensp;Tous les événements</a>',
        )

    @admin.display(description="Agenda")
    def calendar_link(self, obj):
        if not obj or not obj.pk:
            return "-"

        return format_html(
            '<a href="{}" download="{}.ics">'
            "💾&ensp;Télécharger l'agenda des événements de ce type au format .ics"
            "</a>",
            front_url(
                "eventsubtype_ics_calendar", kwargs={"pk": obj.pk}, absolute=True
            ),
            slugify(obj.label),
        )

    @admin.display(description="Prioritaire", boolean=True, ordering="has_priority")
    def priority(self, obj):
        return obj.has_priority

    @admin.display(
        description="Certifiable",
        boolean=True,
        ordering="is_acceptable_for_group_certification",
    )
    def certification(self, obj):
        return obj.is_acceptable_for_group_certification

    @admin.display(
        description="Réservé",
        boolean=True,
        ordering="for_organizer_group_members_only",
    )
    def private(self, obj):
        return obj.for_organizer_group_members_only

    @admin.display(
        description="Co-organisation",
        boolean=True,
        ordering="is_coorganizable",
    )
    def coorganization_allowed(self, obj):
        return obj.is_coorganizable

    @admin.display(
        description="Type de groupe",
        ordering="for_supportgroup_type",
    )
    def for_group_type(self, obj):
        return obj.get_for_supportgroup_type_display()

    @admin.display(description="Groupes", ordering="for_supportgroups")
    def for_groups(self, obj):
        count = obj.for_supportgroups.count()
        if count == 0:
            return "Tous"
        return count

    @admin.display(description="Image par défaut actuelle")
    def default_image_preview(self, obj):
        if not obj or not obj.default_image:
            return "-"

        return mark_safe(
            format_html(
                '<a href="{}"><img src="{}"></a>',
                obj.default_image.url,
                obj.default_image.thumbnail.url,
            )
        )

    @admin.display(description="Icône actuelle")
    def icon_preview(self, obj):
        if not obj or not obj.icon_name:
            return "-"

        background = obj.color or "#f4ed0f"
        color = "white" if obj.color else "#000000"
        split = obj.icon_name.split(":")
        print(split)
        icon_name = split.pop(0)
        icon_variant = split.pop(0) if split else "solid"
        marker_style = (
            "display:inline-flex;"
            "align-items:center;"
            "justify-content:center;"
            "border-radius:50% 50% 50% 0;"
            "transform:rotate(-45deg);"
            "transform-origin:center center;"
            "box-sizing:border-box;"
            "width:50px;"
            "height:50px;"
            "margin-bottom:1rem;"
            f"background:{background};"
            f"color:{color};"
            "border:2px solid white;"
            f"box-shadow:0 0 8px {background};"
            "text-decoration:none;"
        )
        href = f"https://fontawesome.com/icons/{icon_name}?f=classic&s={icon_variant}"

        return mark_safe(
            f'<a target="_blank" href="{href}" style="{marker_style}">'
            f'<i class="fa-{icon_variant} fa-{icon_name} fa-2x" style="transform:rotate(45deg);"></i>'
            "</a>",
        )

    class Media:
        css = {
            "all": (
                "https://media.actionpopulaire.fr/fontawesome/css/all.min.css",
                "https://media.actionpopulaire.fr/fontawesome/css/v4-font-face.min.css",
                "https://media.actionpopulaire.fr/fontawesome/css/v4-shims.min.css",
            )
        }


@admin.register(models.JitsiMeeting)
class JitsiMeetingAdmin(admin.ModelAdmin):
    autocomplete_fields = ("event",)
    readonly_fields = ("start_time", "end_time", "display_link")
    list_display = ("room_name", "event", "start_time", "end_time", "members")

    def members(self, object):
        return object.rsvps.count()

    def display_link(self, object):
        return format_html('<a target="_blank" href="{0}">{0}</a>', object.link)


class IdentifiedGuestInline(admin.StackedInline):
    model = IdentifiedGuest
    verbose_name = "Invité identifié"
    verbose_name_plural = "Invités identifiés"
    fields = readonly_fields = (
        "id",
        "status",
        "payment_link",
        "payment_mode",
        "payment_status",
        "submission_data",
    )

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Paiement", ordering="payment")
    def payment_link(self, obj):
        return display_link(obj.payment)

    @admin.display(description="Mode du paiement")
    def payment_mode(self, obj):
        if not obj or not obj.payment:
            return "-"

        return obj.payment.get_mode_display()

    @admin.display(description="Statut du paiement")
    def payment_status(self, obj):
        if not obj or not obj.payment:
            return "-"

        return obj.payment.get_status_display()

    @admin.display(description="Inscription", ordering="submission")
    def submission_data(self, obj):
        if not obj or not obj.submission:
            return "-"

        return display_json_details(
            obj.submission.data, "Réponse au formulaire d'inscription"
        )


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "person_link",
        "person_created",
        "event_link",
        "payment_link",
        "status",
        "rsvp_created",
        "guest_count",
    )
    fields = readonly_fields = (
        "id",
        "rsvp_created",
        "person_created",
        "status",
        "event_link",
        "person_link",
        "person_contact_phone",
        "payment_link",
        "payment_mode",
        "payment_status",
        "submission_data",
        "guest_count",
    )
    search_fields = ("person__search", "event__name")
    list_filter = (RelatedEventFilter, "status", RSVPGuestFilter)
    inlines = (IdentifiedGuestInline,)

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

    @admin.display(description="Personne", ordering="person")
    def person_link(self, obj):
        return display_link(obj.person)

    @admin.display(description="Inscrit·e sur AP depuis le", ordering="person__created")
    def person_created(self, obj):
        return obj.person.created.strftime("%d/%m/%Y")

    @admin.display(description="Date d'inscription", ordering="created")
    def rsvp_created(self, obj):
        return obj.created.strftime("%d/%m/%Y")

    @admin.display(description="Numéro de téléphone")
    def person_contact_phone(self, obj):
        return obj.person.contact_phone

    @admin.display(description="Événement", ordering="event")
    def event_link(self, obj):
        return display_link(obj.event)

    @admin.display(description="Paiement", ordering="payment")
    def payment_link(self, obj):
        return display_link(obj.payment)

    @admin.display(description="Mode du paiement")
    def payment_mode(self, obj):
        if not obj or not obj.payment:
            return "-"

        return obj.payment.get_mode_display()

    @admin.display(description="Statut du paiement")
    def payment_status(self, obj):
        if not obj or not obj.payment:
            return "-"

        return obj.payment.get_status_display()

    @admin.display(description="Inscription", ordering="form_submission")
    def submission_data(self, obj):
        if not obj.form_submission:
            return "-"

        return display_json_details(
            obj.form_submission.data, "Réponse au formulaire d'inscription"
        )

    @admin.display(description="Invités")
    def guest_count(self, obj):
        return obj.guests

    @admin.display(description="")
    def filter_by_event_button(self, obj):
        return format_html(
            '<a class="button default" style="color: white;" href="{link}?event={event_id}">Voir uniquement cet événement</a>',
            link=reverse("admin:events_rsvp_changelist"),
            event_id=str(obj.event_id),
        )

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
