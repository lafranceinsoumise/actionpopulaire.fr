import json
import secrets
from copy import deepcopy
from functools import partial
from urllib.parse import urlencode

import django_otp
from django.contrib import admin, messages
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.utils import display_for_value, unquote
from django.contrib.admin.views.main import ERROR_FLAG
from django.contrib.gis.admin import OSMGeoAdmin
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Count, Max, Func, Value
from django.db.models.functions import Concat, Substr
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse, SimpleTemplateResponse
from django.urls import reverse, path
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilter

from agir.authentication.models import Role
from agir.elus.models import types_elus
from agir.lib.admin.filters import (
    DepartementListFilter,
    RegionListFilter,
    CirconscriptionLegislativeFilter,
)
from agir.lib.admin.panels import CenterOnFranceMixin, DisplayContactPhoneMixin
from agir.lib.admin.utils import display_link
from agir.lib.utils import generate_token_params, front_url
from agir.people.actions.stats import get_statistics_for_queryset
from agir.people.admin import filters
from agir.people.admin.actions import (
    export_people_to_csv,
    export_liaisons_to_csv,
    unsubscribe_from_all_newsletters,
    bulk_add_tag,
    remove_from_liaisons,
)
from agir.people.admin.forms import PersonAdminForm, PersonFormForm
from agir.people.admin.inlines import (
    MembershipInline,
    EmailInline,
    PersonQualificationInline,
)
from agir.people.admin.views import (
    FormSubmissionViewsMixin,
    AddPersonEmailView,
    MergePersonsView,
    PersonFormSandboxView,
)
from agir.people.models import (
    Person,
    PersonTag,
    PersonQualification,
    Qualification,
)
from agir.people.person_forms.display import default_person_form_display
from agir.people.person_forms.models import PersonForm, PersonFormSubmission

__all__ = [
    "PersonAdmin",
    "PersonTagAdmin",
    "PersonFormAdmin",
    "PersonFormSubmissionAdmin",
    "ContactAdmin",
    "LiaisonAdmin",
    "QualificationAdmin",
    "PersonQualificationAdmin",
]


@admin.register(Person)
class PersonAdmin(DisplayContactPhoneMixin, CenterOnFranceMixin, OSMGeoAdmin):
    list_display = (
        "__str__",
        "display_contact_phone",
        "is_political_support",
        "newsletters",
        "location_city",
        "location_zip",
        "created",
        "role_link",
    )
    list_display_links = ("__str__",)
    form = PersonAdminForm

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "display_name",
                    "primary_email",
                    "public_email",
                    "connection_params",
                    "disabled_account",
                    "role_link",
                    "role_totp_link",
                )
            },
        ),
        (_("Dates"), {"fields": ("created", "modified", "last_login")}),
        (
            _("Paramètres mails"),
            {
                "fields": (
                    "newsletters",
                    "unsubscribe_from_all_newsletters",
                    "subscribed_sms",
                    "campaigns_link",
                )
            },
        ),
        (
            _("Paramètres de participation"),
            {"fields": ("is_political_support", "draw_participation")},
        ),
        (
            _("Profil"),
            {"fields": ("gender", "date_of_birth", "tags", "mandats", "image")},
        ),
        (
            _("Contact et adresse"),
            {
                "fields": (
                    "contact_phone",
                    "contact_phone_status",
                    "location_name",
                    "location_address1",
                    "location_address2",
                    "location_city",
                    "location_zip",
                    "location_departement_id",
                    "location_state",
                    "location_country",
                    "location_citycode",
                    "action_radius",
                    "coordinates",
                    "coordinates_type",
                    "coordinates_value",
                    "redo_geocoding",
                )
            },
        ),
        (_("Meta"), {"fields": ("meta", "form_submissions_link")}),
        (
            _("Comité de Respect des Principes"),
            {"permission": "people.crp", "fields": ("crp",)},
        ),
        (_("ÉVÉNEMENTS"), {"fields": ("rsvp_link", "rsvp_event_link")}),
    )

    readonly_fields = (
        "primary_email",
        "connection_params",
        "created",
        "modified",
        "last_login",
        "role_link",
        "role_totp_link",
        "unsubscribe_from_all_newsletters",
        "campaigns_link",
        "supportgroups",
        "events",
        "location_departement_id",
        "coordinates_type",
        "coordinates_value",
        "mandats",
        "location_citycode",
        "form_submissions_link",
        "rsvp_link",
        "rsvp_event_link",
    )

    list_filter = (
        filters.SegmentFilter,
        filters.BouncedEmailFilter,
        CirconscriptionLegislativeFilter,
        DepartementListFilter,
        RegionListFilter,
        "is_political_support",
        "subscribed_sms",
        "draw_participation",
        "gender",
        filters.TagListFilter,
        filters.AnimateMoreThanOneGroup,
        ("created", DateRangeFilter),
    )

    inlines = (PersonQualificationInline, MembershipInline, EmailInline)

    autocomplete_fields = ("tags",)

    # doit être non vide pour afficher le formulaire de recherche,
    # mais n'est en réalité pas utilisé pour déterminer les champs
    # de recherche
    search_fields = ["search", "contact_phone"]

    actions = (export_people_to_csv, bulk_add_tag)

    def get_fieldsets(self, request, obj=None):
        fieldsets = deepcopy(super().get_fieldsets(request, obj))
        authorized_fieldsets = []
        for key, props in fieldsets:
            permission = props.pop("permission", False)
            if not permission or request.user.has_perm(permission):
                authorized_fieldsets.append((key, props))
        return tuple(authorized_fieldsets)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.search(search_term)

        use_distinct = False

        return queryset, use_distinct

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("public_email")
            .prefetch_related("emails", "form_submissions")
        )

    def coordinates_value(self, obj):
        return f"{obj.coordinates.coords[1]}, {obj.coordinates.coords[0]}"

    coordinates_value.short_description = _("Coordoonées")

    def role_link(self, obj):
        if not obj or not obj.pk:
            return "-"

        if obj.role_id is not None:
            return format_html(
                '<a href="{link}">{text}</a>',
                link=reverse("admin:authentication_role_change", args=[obj.role_id]),
                text=_("Voir le rôle"),
            )

        return format_html(
            'Pas de compte associé à cette personne&emsp;<a href="{}" class="button">Créer un rôle</a>',
            reverse(
                "admin:people_person_ensure_role_exists",
                kwargs={"pk": str(obj.pk)},
            ),
        )

    role_link.short_description = _("Rôle")

    def role_totp_link(self, obj):
        if obj.role is not None:
            return format_html_join(
                mark_safe("<br>"),
                '<a href="{}">{}</a>',
                (
                    (
                        reverse("admin:otp_totp_totpdevice_change", args=[device.id]),
                        device.name,
                    )
                    for device in django_otp.devices_for_user(obj.role, confirmed=True)
                ),
            )
        return "-"

    role_totp_link.short_description = _(
        "Lien vers les téléphones Authenticator enregistrés"
    )

    def unsubscribe_from_all_newsletters(self, obj):
        if not obj or not obj.pk:
            return "-"
        return format_html(
            '<a href="{}" class="button">Désinscrire de tous les envois d\'e-mails et de notifications push</a>',
            reverse(
                "admin:people_person_unsubscribe_from_all_newsletters",
                kwargs={"pk": str(obj.pk)},
            ),
        )

    unsubscribe_from_all_newsletters.short_description = "Désinscription"

    def campaigns_link(self, obj):
        return format_html(
            '<a href="{}" class="button">Voir l\'historique</a>',
            reverse("admin:nuntius_campaignsentevent_changelist")
            + "?subscriber_id__exact="
            + str(obj.pk),
        )

    campaigns_link.short_description = "Campagnes envoyées"

    def rsvp_link(self, obj):
        if not obj or not obj.pk:
            return "-"

        return format_html(
            '<a href="{}" class="button">Voir les participations aux événements</a>',
            reverse("admin:events_rsvp_changelist") + f"?person_id={str(obj.pk)}",
        )

    rsvp_link.short_description = "RSVP"

    def rsvp_event_link(self, obj):
        if not obj or not obj.pk:
            return "-"

        return format_html(
            '<a href="{}" class="button">Voir les événements</a>',
            reverse("admin:events_event_changelist") + f"?participant_id={str(obj.pk)}",
        )

    rsvp_event_link.short_description = "Événements"

    def connection_params(self, obj):
        if not obj or not obj.pk:
            return "-"

        return format_html(
            "<pre style='margin: 0; padding: 0;'>?{params}</pre>"
            '<p style="padding: 8px 0;"><a class="button" href="{invalidate_link}">Invalider les liens</a></p>'
            "<div style='margin: 0; padding-left: 0;' class='help'>"
            "À copier/coller à la fin d'une URL pour obtenir un lien qui connecte automatiquement"
            "</div>",
            params=urlencode(generate_token_params(obj)),
            invalidate_link=reverse(
                "admin:people_person_invalidate_link", args=(obj.pk,)
            ),
        )

    connection_params.short_description = _("Paramètres de connexion")

    def last_login(self, obj):
        if obj.role_id:
            return display_for_value(obj.role.last_login, "-")
        else:
            return "-"

    last_login.short_description = Role._meta.get_field("last_login").verbose_name

    @admin.display(description="Adresse principale")
    def primary_email(self, obj):
        if obj._state.adding:
            return "-"

        primary_email = obj.primary_email
        emails = obj.emails.all()

        args = [
            (email.id, " selected" if email == primary_email else "", email.address)
            for email in emails
        ]

        options = format_html_join("", '<option value="{}"{}>{}</option>', args)

        return format_html(
            '<select name="primary_email">{options}</select>&emsp;'
            '<a class="button" href="{add_email_link}">Ajouter une adresse</a>'
            '<div class="help" style="margin: 0; padding: 0;">'
            "L'adresse email utilisée pour communiquer avec la personne (campagnes, emails automatiques, etc.)"
            "</div>",
            add_email_link=reverse("admin:people_person_addemail", args=[obj.pk]),
            options=options,
        )

    def mandats(self, obj):
        if obj is None:
            return "-"

        mandats = []

        for attr, model in list(types_elus.items()):
            for m in model.objects.filter(person=obj):
                mandats.append(
                    (
                        reverse(
                            f"admin:elus_mandat{attr.replace('_', '')}_change",
                            args=(m.id,),
                        ),
                        m.titre_complet(conseil_avant=True),
                    )
                )

        if not mandats:
            return "-"

        return format_html_join(mark_safe("<br>"), '<a href="{}">{}</a>', mandats)

    def form_submissions_link(self, obj):
        return format_html(
            '<a href="{}?person_id={}" class="button">Voir les formulaires remplis</a>',
            reverse("admin:people_personformsubmission_changelist"),
            str(obj.pk),
        )

    form_submissions_link.short_description = "Formulaires"

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/invalidate_links/",
                self.admin_site.admin_view(self.invalidate_link_view),
                name="people_person_invalidate_link",
            ),
            path(
                "<uuid:pk>/add_email/",
                self.admin_site.admin_view(
                    AddPersonEmailView.as_view(model_admin=self)
                ),
                name="people_person_addemail",
            ),
            path(
                "merge_persons/",
                self.admin_site.admin_view(
                    partial(MergePersonsView.as_view(), model_admin=self)
                ),
                name="people_person_merge",
            ),
            path(
                "statistiques/",
                self.statistics_view,
                name="people_person_statistics",
            ),
            path(
                "<uuid:pk>/unsubscribe-from-all-newsletters/",
                self.unsubscribe_from_all_newsletter_view,
                name="people_person_unsubscribe_from_all_newsletters",
            ),
            path(
                "<uuid:pk>/ensure-role-exists/",
                self.ensure_role_exists,
                name="people_person_ensure_role_exists",
            ),
        ] + super().get_urls()

    def invalidate_link_view(self, request, pk):
        person = get_object_or_404(Person, pk=pk)

        person.auto_login_salt = secrets.token_urlsafe(30)
        person.save()

        messages.add_message(
            request=request,
            level=messages.SUCCESS,
            message="Les liens de connexion de cette personne ont été correctement invalidés.",
        )

        return HttpResponseRedirect(reverse("admin:people_person_change", args=(pk,)))

    def statistics_view(self, request):
        try:
            cl = self.get_changelist_instance(request)
        except IncorrectLookupParameters:
            if ERROR_FLAG in request.GET:
                return SimpleTemplateResponse(
                    "admin/invalid_setup.html",
                    {
                        "title": _("Database error"),
                    },
                )
            return HttpResponseRedirect(request.path + "?" + ERROR_FLAG + "=1")

        queryset = cl.get_queryset(request)
        statistics = get_statistics_for_queryset(queryset)
        chart_data = (
            queryset.exclude(meta__subscriptions__NSP__date__isnull=True)
            .annotate(
                subscription_datetime=Func(
                    "meta",
                    Value("subscriptions"),
                    Value("NSP"),
                    Value("date"),
                    function="jsonb_extract_path_text",
                )
            )
            .annotate(
                subscription_date=Concat(
                    Substr("subscription_datetime", 1, 10), Value("T00:00:00Z")
                )
            )
            .values("subscription_date")
            .annotate(y=Count("id"))
            .order_by("subscription_date")
        )

        context = {
            **self.admin_site.each_context(request),
            "title": "Statistiques",
            "opts": self.model._meta,
            "cl": cl,
            "media": self.media,
            "preserved_filters": self.get_preserved_filters(request),
            "chart_data": json.dumps(list(chart_data), cls=DjangoJSONEncoder),
            "changelist_link": f'{reverse("admin:people_person_changelist")}?{request.GET.urlencode()}',
            "statistics": statistics,
        }

        return TemplateResponse(
            request,
            "admin/people/person/statistics.html",
            context,
        )

    def unsubscribe_from_all_newsletter_view(self, request, pk):
        person = get_object_or_404(Person, pk=pk)

        unsubscribe_from_all_newsletters(person)

        messages.add_message(
            request=request,
            level=messages.SUCCESS,
            message="Cette personne a été désinscrite de tous les envois d'emails et de notifications push",
        )

        return HttpResponseRedirect(reverse("admin:people_person_change", args=(pk,)))

    def ensure_role_exists(self, request, pk):
        person = get_object_or_404(Person, pk=pk)
        person.ensure_role_exists()
        messages.add_message(
            request=request,
            level=messages.SUCCESS,
            message="Un rôle a été créé pour cette personne",
        )
        return HttpResponseRedirect(reverse("admin:people_person_change", args=(pk,)))

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj) or (
            request.resolver_match.url_name == "autocomplete"
            and request.user.has_perm("people.select_person")
        )

    def has_export_permission(self, request):
        return request.user.has_perm("people.export_people")

    def has_bulk_add_tag_permission(self, request):
        return request.user.has_perm("people.change_person") and request.user.has_perm(
            "people.view_persontag"
        )

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context[
            "statistics_link"
        ] = f'{reverse("admin:people_person_statistics")}?{request.GET.urlencode()}'

        if (
            hasattr(request, "POST")
            and request.POST.get("action", None)
            and not request.POST.getlist(admin.helpers.ACTION_CHECKBOX_NAME)
        ):
            # If no item is selected and action select_across is set to True
            # allow applying the action to all items that match the current view
            # filters (optionally limiting the number of items to a maximum value)
            select_across = False
            try:
                action = self.get_actions(request)[request.POST["action"]][0]
                select_across = action.select_across
            except (KeyError, AttributeError):
                pass

            if select_across:
                items = (
                    self.get_changelist_instance(request)
                    .get_queryset(request)
                    .values_list("id", flat=True)
                )

                if hasattr(action, "max_items"):
                    items[: action.max_items]

                post = request.POST.copy()
                post.setlist(
                    admin.helpers.ACTION_CHECKBOX_NAME,
                    items,
                )
                request.POST = post

        return super().changelist_view(request, extra_context)

    def save_form(self, request, form, change):
        return form.save(commit=False, request=request)

    class Media:
        pass


@admin.register(PersonTag)
class PersonTagAdmin(admin.ModelAdmin):
    list_display = ("label", "exported")

    search_fields = ("label",)


@admin.register(PersonForm)
class PersonFormAdmin(FormSubmissionViewsMixin, admin.ModelAdmin):
    form = PersonFormForm
    save_as = True
    search_fields = ("title",)
    list_display = (
        "title",
        "slug_link",
        "published",
        "created",
        "submissions_number",
        "last_submission",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "published",
                    "start_time",
                    "end_time",
                    "editable",
                    "allow_anonymous",
                    "send_answers_to",
                    "required_tags",
                    "lien_feuille_externe",
                    "segment",
                    "linked_event",
                )
            },
        ),
        (
            _("Soumissions"),
            {
                "fields": (
                    "submissions_number",
                    "person_count",
                    "simple_link",
                    "action_buttons",
                    "result_url",
                    "campaign_template",
                )
            },
        ),
        (_("Champs"), {"fields": ("tags", "main_question", "custom_fields", "config")}),
        (
            _("Textes"),
            {
                "fields": (
                    "description",
                    "confirmation_note",
                    "send_confirmation",
                    "unauthorized_message",
                    "before_message",
                    "after_message",
                )
            },
        ),
        (
            _("Meta"),
            {"fields": ("short_description", "meta_image")},
        ),
    )

    readonly_fields = (
        "submissions_number",
        "person_count",
        "simple_link",
        "action_buttons",
        "last_submission",
        "result_url",
        "linked_event",
    )
    autocomplete_fields = ("required_tags", "segment", "tags", "campaign_template")

    @admin.display(description="Dernière réponse", ordering="last_submission")
    def last_submission(self, obj):
        last_submission = obj.submissions.last()
        if last_submission is None:
            return mark_safe("-")
        return last_submission.created

    @admin.display(description="Événement")
    def linked_event(self, obj):
        if obj and obj.subscription_form_event:
            return display_link(
                obj.subscription_form_event,
                text=f"[INSCRIPTION] {obj.subscription_form_event}",
            )

        if obj and obj.volunteer_application_form_event:
            return display_link(
                obj.volunteer_application_form_event,
                text=f"[APPEL À VOLONTAIRES] {obj.volunteer_application_form_event}",
            )

        return "-"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(
            submissions_number=Count("submissions", distinct=True),
            person_count=Count("submissions__person_id", distinct=True),
            last_submission=Max("submissions__created"),
        )

    def get_urls(self):
        return [
            path(
                "<int:pk>/view_results/",
                self.admin_site.admin_view(self.view_results),
                name="people_personform_view_results",
            ),
            path(
                "<int:pk>/download_results/",
                self.admin_site.admin_view(self.download_results),
                name="people_personform_download_results",
            ),
            path(
                "<int:pk>/create_result_url/",
                self.admin_site.admin_view(self.create_result_url),
                name="people_personform_create_result_url",
            ),
            path(
                "<int:pk>/clear_result_url/",
                self.admin_site.admin_view(partial(self.create_result_url, clear=True)),
                name="people_personform_clear_result_url",
            ),
            path(
                "sandbox/",
                self.admin_site.admin_view(
                    PersonFormSandboxView.as_view(model_admin=self)
                ),
                name="people_personform_sandbox",
            ),
            path(
                "<int:pk>/reset_feuille_externe/",
                self.admin_site.admin_view(self.reset_feuille_externe),
                name="people_personform_reset_feuille_externe",
            ),
        ] + super().get_urls()

    def slug_link(self, obj):
        if obj.slug:
            return format_html(
                '<a href="{}">{}</a>',
                front_url("view_person_form", args=(obj.slug,)),
                obj.slug,
            )
        else:
            return "-"

    slug_link.short_description = "Slug"

    def action_buttons(self, obj):
        if obj._state.adding or obj.submissions_number == 0:
            return "-"

        html = format_html(
            '<a href="{view_results_link}" class="button">Voir les résultats</a>'
            ' <a href="{download_results_link}" class="button">Télécharger les résultats</a>',
            view_results_link=reverse(
                "admin:people_personform_view_results", args=(obj.pk,)
            ),
            download_results_link=reverse(
                "admin:people_personform_download_results", args=(obj.pk,)
            ),
        )

        if obj.lien_feuille_externe:
            html += format_html(
                ' <a href="{reset_feuille_externe}" class="button danger">Réinitialiser la feuille externe</a>',
                reset_feuille_externe=reverse(
                    "admin:people_personform_reset_feuille_externe", args=(obj.pk,)
                ),
            )

        return html

    action_buttons.short_description = _("Actions")

    def simple_link(self, obj):
        if obj.slug:
            return format_html('<a href="{0}">{0}</a>', obj.front_url)
        else:
            return "-"

    simple_link.short_description = "Lien vers le formulaire"

    def result_url(self, obj):
        if obj._state.adding:
            return "-"

        if obj.result_url_uuid:
            return format_html(
                '<a href="{url}">{url}</a> <a href="{change_url}" class="button">Changer l\'URL</a>'
                ' <a href="{clear_url}" class="button">Supprimer l\'URL</a>',
                url=front_url(
                    "person_form_private_submissions", args=(obj.result_url_uuid,)
                ),
                change_url=reverse(
                    "admin:people_personform_create_result_url", args=(obj.pk,)
                ),
                clear_url=reverse(
                    "admin:people_personform_clear_result_url", args=(obj.pk,)
                ),
            )

        return format_html(
            '<em>Pas d\'URL pour le moment</em> <a href="{change_url}" class="button">Créer une URL</a>',
            change_url=reverse(
                "admin:people_personform_create_result_url", args=(obj.pk,)
            ),
        )

    result_url.short_description = "Lien vers les résultats accessible sans connexion"
    result_url.help_text = (
        "Ce lien permet d'accéder à l'ensemble des résultats de ce formulaire sans avoir besoin de se connecter."
        " Faites bien attention en le transmettant à des personnes tierces."
    )

    @admin.display(description="Nombre de réponses")
    def submissions_number(self, obj):
        return obj.submissions_number

    @admin.display(description="Nombre de personnes")
    def person_count(self, obj):
        return obj.person_count


@admin.register(PersonFormSubmission)
class PersonFormSubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ("person",)
    search_fields = ("person__search", "form__title")
    list_display = ("created", "form_link", "person_link")

    def person_link(self, instance):
        if not instance.person:
            return "-"

        return format_html(
            '<a href="{link}">{person}</a>',
            person=str(instance.person),
            link=reverse("admin:people_person_change", args=[instance.person.id]),
        )

    person_link.short_description = "Personne"

    def form_link(self, instance):
        if not instance.form:
            return "-"

        return format_html(
            '<a href="{link}">{form}</a>',
            form=str(instance.form),
            link=reverse("admin:people_personform_change", args=[instance.form.id]),
        )

    form_link.short_description = "Formulaire"

    def has_add_permission(self, request):
        return False

    def return_to_form_results(self):
        return HttpResponseRedirect(
            reverse("admin:people_personform_view_results", args=[self.personform.pk])
        )

    def delete_view(self, request, object_id, extra_context=None):
        submission = self.get_object(request, unquote(object_id))
        if submission is None:
            raise Http404()
        self.personform = submission.form
        return super().delete_view(request, object_id, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        submission = self.get_object(request, unquote(object_id))
        if submission is None:
            raise Http404()
        self.personform = submission.form
        return super().change_view(request, object_id, form_url, extra_context)

    def detail_view(self, request, object_id):
        self.object = self.get_object(request, unquote(object_id))
        if self.object is None:
            raise Http404()
        if not self.has_view_permission(request, self.object):
            raise PermissionDenied
        return TemplateResponse(
            request=request,
            template="admin/personforms/detail.html",
            context={
                "submission_data": default_person_form_display.get_formatted_submission(
                    self.object
                ),
                "submission": self.object,
                "title": "Détails",
                "opts": PersonForm._meta,
                "add": False,
                "change": False,
                "is_popup": False,
                "save_as": False,
                "has_change_permission": True,
                "has_view_permission": True,
                "has_delete_permission": False,
                "show_close": False,
            },
        )

    def response_delete(self, request, obj_display, obj_id):
        return self.return_to_form_results()

    def response_post_save_change(self, request, obj):
        return self.return_to_form_results()

    def get_urls(self):
        return [
            path(
                "<object_id>/detail/",
                self.admin_site.admin_view(self.detail_view),
                name="people_personformsubmission_detail",
            )
        ] + super().get_urls()

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("person", "form")


class Contact(Person):
    class Meta:
        proxy = True


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_address",
        "is_liaison",
        "is_political_support",
        "created",
        "subscriber",
    )
    list_filter = (
        filters.SegmentFilter,
        "is_political_support",
        ("created", DateRangeFilter),
    )
    search_fields = ["search", "contact_phone"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def name(self, obj):
        return format_html(
            '<a href="{link}">{person}</a>',
            person=str(obj),
            link=reverse("admin:people_person_change", args=[obj.id]),
        )

    name.short_description = "Nom du contact"

    def short_address(self, obj):
        return obj.short_address

    short_address.short_description = "Adresse"

    def is_liaison(self, obj):
        return obj.is_liaison

    is_liaison.short_description = "Relai insoumis"
    is_liaison.boolean = True

    def subscriber(self, obj):
        subscriber_id = obj.meta["subscriptions"]["AP"]["subscriber"]
        subscriber = Person.objects.filter(pk=subscriber_id).first()
        if subscriber:
            return format_html(
                '<a href="{link}">{person}</a>',
                person=str(subscriber),
                link=reverse("admin:people_person_change", args=[subscriber.id]),
            )

    subscriber.short_description = "Personne à l'origine de l'ajout"

    def get_queryset(self, *args, **kwargs):
        return (
            super()
            .get_queryset(*args, **kwargs)
            .filter(meta__subscriptions__AP__subscriber__isnull=False)
        )

    class Media:
        pass


class Liaison(Person):
    class Meta:
        proxy = True
        verbose_name = "relai insoumis"
        verbose_name_plural = "relais insoumis"


@admin.register(Liaison)
class LiaisonAdmin(admin.ModelAdmin):
    list_display = ("name", "short_address", "liaison_date", "created")
    list_filter = (
        filters.SegmentFilter,
        CirconscriptionLegislativeFilter,
        DepartementListFilter,
        RegionListFilter,
    )
    search_fields = ["search", "contact_phone"]
    actions = (export_liaisons_to_csv, remove_from_liaisons)

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm("people.view_liaison")

    def has_export_permission(self, request):
        return request.user.has_perm("people.export_people")

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm("people.change_liaison")

    def name(self, obj):
        return format_html(
            '<a href="{link}">{person}</a>',
            person=str(obj),
            link=reverse("admin:people_person_change", args=[obj.id]),
        )

    name.short_description = "Personne"

    def short_address(self, obj):
        return obj.short_address

    short_address.short_description = "Adresse"

    def liaison_date(self, obj):
        return obj.liaison_date

    liaison_date.short_description = "Relai insoumis depuis"
    liaison_date.admin_order_field = "liaison_date"

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).liaisons()

    class Media:
        pass


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ("label", "description", "active_count", "total_count")
    inlines = (PersonQualificationInline,)
    search_fields = ("label",)

    @admin.display(description="En cours")
    def active_count(self, obj):
        return obj.person_qualifications.effective().count()

    @admin.display(description="Total")
    def total_count(self, obj):
        return obj.person_qualifications.count()


@admin.register(PersonQualification)
class PersonQualificationAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "is_effective",
                    "qualification",
                    "person",
                    "supportgroup",
                    "start_time",
                    "end_time",
                    "description",
                )
            },
        ),
    )
    list_display = (
        "id",
        "person_link",
        "supportgroup_link",
        "qualification_link",
        "interval",
        "is_effective",
    )
    search_fields = ("person__search", "qualification__label", "supportgroup__name")
    list_filter = (
        filters.PersonQualificationStatusListFilter,
        filters.QualificationListFilter,
        filters.PersonQualificationSupportGroupListFilter,
    )
    autocomplete_fields = ("person", "qualification", "supportgroup")
    readonly_fields = ("id", "is_effective")
    create_only_fields = ("person", "qualification", "supportgroup")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not obj:
            return readonly_fields

        return readonly_fields + self.create_only_fields

    @admin.display(description="Type de statut", ordering="qualification")
    def qualification_link(self, obj):
        return display_link(obj.qualification)

    @admin.display(description="Personne", ordering="person")
    def person_link(self, obj):
        return display_link(obj.person)

    @admin.display(description="Groupe", ordering="supportgroup")
    def supportgroup_link(self, obj):
        return display_link(obj.supportgroup)

    @admin.display(description="Durée", ordering="start_time")
    def interval(self, obj):
        return obj.get_range_display()

    @admin.display(description="En cours", boolean=True)
    def is_effective(self, obj):
        return obj and obj.is_effective

    class Media:
        pass
