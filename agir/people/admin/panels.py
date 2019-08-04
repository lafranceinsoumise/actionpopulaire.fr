import secrets
from functools import partial
from urllib.parse import urlencode

import django_otp
from django.contrib import admin, messages
from django.contrib.admin.utils import display_for_value, unquote
from django.contrib.gis.admin import OSMGeoAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Max
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from agir.api.admin import admin_site
from agir.authentication.models import Role
from agir.lib.admin import (
    DisplayContactPhoneMixin,
    CenterOnFranceMixin,
    DepartementListFilter,
    RegionListFilter,
)
from agir.lib.utils import generate_token_params, front_url
from agir.people.admin.forms import PersonAdminForm, PersonFormForm
from agir.people.admin.inlines import RSVPInline, MembershipInline, EmailInline
from agir.people.admin.views import (
    FormSubmissionViewsMixin,
    AddPersonEmailView,
    MergePersonsView,
)
from agir.people.models import Person, PersonTag
from agir.people.person_forms.display import default_person_form_display
from agir.people.person_forms.models import PersonForm, PersonFormSubmission
from agir.people.tasks import update_person_mailtrain

__all__ = [
    "PersonAdmin",
    "PersonTagAdmin",
    "PersonFormAdmin",
    "PersonFormSubmissionAdmin",
]


@admin.register(Person, site=admin_site)
class PersonAdmin(DisplayContactPhoneMixin, CenterOnFranceMixin, OSMGeoAdmin):
    list_display = (
        "__str__",
        "display_contact_phone",
        "is_insoumise",
        "subscribed",
        "role_link",
        "created",
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
                    "primary_email",
                    "connection_params",
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
                    "subscribed",
                    "subscribed_sms",
                    "event_notifications",
                    "group_notifications",
                )
            },
        ),
        (
            _("Paramètres de participation"),
            {"fields": ("is_insoumise", "draw_participation")},
        ),
        (_("Profil"), {"fields": ("gender", "date_of_birth", "tags", "mandates")}),
        (
            _("Contact et adresse"),
            {
                "fields": (
                    "contact_phone",
                    "location_name",
                    "location_address",
                    "location_address1",
                    "location_address2",
                    "location_city",
                    "location_zip",
                    "location_state",
                    "location_country",
                    "coordinates",
                    "coordinates_type",
                    "redo_geocoding",
                )
            },
        ),
        (_("Meta"), {"fields": ("meta",)}),
    )

    readonly_fields = (
        "primary_email",
        "connection_params",
        "created",
        "modified",
        "last_login",
        "role_link",
        "role_totp_link",
        "supportgroups",
        "events",
        "coordinates_type",
    )

    list_filter = (
        DepartementListFilter,
        RegionListFilter,
        ("is_insoumise", admin.BooleanFieldListFilter),
        ("subscribed", admin.BooleanFieldListFilter),
        ("subscribed_sms", admin.BooleanFieldListFilter),
        ("draw_participation", admin.BooleanFieldListFilter),
        "gender",
        "tags",
    )

    inlines = (RSVPInline, MembershipInline, EmailInline)

    autocomplete_fields = ("tags",)

    # doit être non vide pour afficher le formulaire de recherche,
    # mais n'est en réalité pas utilisé pour déterminer les champs
    # de recherche
    search_fields = ["search", "contact_phone"]

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.full_text_search(search_term)

        use_distinct = False

        return queryset, use_distinct

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("emails")

    def role_link(self, obj):
        return format_html(
            '<a href="{link}">{text}</a>',
            link=reverse("admin:authentication_role_change", args=[obj.role_id]),
            text=_("Voir le rôle"),
        )

    role_link.short_description = _("Lien vers le rôle")

    def role_totp_link(self, obj):
        return format_html_join(
            mark_safe("<br>"),
            '<a href="{}">{}</a>',
            (
                (
                    reverse("admin:otp_totp_totpdevice_change", args=[device.id]),
                    device.name,
                )
                for device in django_otp.devices_for_user(obj.role, confirmed=False)
            ),
        )

    role_totp_link.short_description = _(
        "Lien vers les téléphones Authenticator enregistrés"
    )

    def connection_params(self, obj):
        if obj.pk:
            return format_html(
                '{params} <a class="button" href="{invalidate_link}">Invalider les liens</a>',
                params=urlencode(generate_token_params(obj)),
                invalidate_link=reverse(
                    "admin:people_person_invalidate_link", args=(obj.pk,)
                ),
            )
        else:
            return "-"

    connection_params.short_description = _("Paramètres de connexion")
    connection_params.help_text = _(
        "A copier/coller à la fin d'une url agir pour obtenir un lien qui connecte automatiquement."
    )

    def last_login(self, obj):

        if obj.role_id:
            return display_for_value(obj.role.last_login, "-")
        else:
            return "-"

    last_login.short_description = Role._meta.get_field("last_login").verbose_name

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
            '<select name="primary_email">{options}</select> <a class="button" href="{add_email_link}">Ajouter une adresse</a>',
            add_email_link=reverse("admin:people_person_addemail", args=[obj.pk]),
            options=options,
        )

    primary_email.short_description = "Adresse principale"

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
                    partial(AddPersonEmailView.as_view(), model_admin=self)
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


@admin.register(PersonTag, site=admin_site)
class PersonTagAdmin(admin.ModelAdmin):
    list_display = ("label", "exported")

    actions = ("set_as_exported", "set_as_not_exported", "export_now")
    search_fields = ("label",)

    def set_as_exported(self, request, queryset):
        queryset.update(exported=True)

    set_as_exported.short_description = _("Exporter ces tags")

    def set_as_not_exported(self, request, queryset):
        queryset.update(exported=False)

    set_as_not_exported.short_description = _("Ne plus exporter")

    def export_now(self, request, queryset):
        persons = Person.objects.filter(tags__in=queryset).distinct()
        count = persons.count()

        if count > 5000:
            self.message_user(
                request,
                "Vous ne pouvez synchroniser plus de 5000 personnes de cette manière.",
                level=messages.ERROR,
            )

            return
        else:
            update_person_mailtrain.map(persons)
            self.message_user(
                request,
                f"Synchronisation en cours de {count} personnes. Cela peut prendre un moment.",
                level=messages.SUCCESS,
            )

    export_now.short_description = "Lancer une synchronisaton maintenant"


@admin.register(PersonForm, site=admin_site)
class PersonFormAdmin(FormSubmissionViewsMixin, admin.ModelAdmin):
    form = PersonFormForm
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
                )
            },
        ),
        (
            _("Soumissions"),
            {
                "fields": (
                    "submissions_number",
                    "simple_link",
                    "action_buttons",
                    "result_url",
                )
            },
        ),
        (_("Champs"), {"fields": ("main_question", "tags", "custom_fields", "config")}),
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
    )

    readonly_fields = (
        "submissions_number",
        "simple_link",
        "action_buttons",
        "last_submission",
        "result_url",
    )
    autocomplete_fields = ("required_tags", "tags")

    def last_submission(self, obj):
        last_submission = obj.submissions.last()
        if last_submission is None:
            return mark_safe("-")
        return last_submission.created

    last_submission.short_description = "Dernière réponse"
    last_submission.admin_order_field = "last_submission"

    def get_readonly_fields(self, request, obj=None):
        pass
        if obj is not None:
            return self.readonly_fields + ("editable",)
        return self.readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(
            submissions_number=Count("submissions"),
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
        ] + super().get_urls()

    def slug_link(self, object):
        if object.slug:
            return format_html(
                '<a href="{}">{}</a>',
                front_url("view_person_form", args=(object.slug,)),
                object.slug,
            )
        else:
            return "-"

    slug_link.short_description = "Slug"

    def action_buttons(self, object):
        if object._state.adding:
            return "-"
        else:
            return format_html(
                '<a href="{view_results_link}" class="button">Voir les résultats</a>'
                ' <a href="{download_results_link}" class="button">Télécharger les résultats</a>',
                view_results_link=reverse(
                    "admin:people_personform_view_results", args=(object.pk,)
                ),
                download_results_link=reverse(
                    "admin:people_personform_download_results", args=(object.pk,)
                ),
            )

    action_buttons.short_description = _("Actions")

    def simple_link(self, object):
        if object.slug:
            return format_html(
                '<a href="{0}">{0}</a>',
                front_url("view_person_form", args=(object.slug,)),
            )
        else:
            return "-"

    simple_link.short_description = "Lien vers le formulaire"

    def result_url(self, object):
        if object._state.adding:
            return "-"

        if object.result_url_uuid:
            return format_html(
                '<a href="{url}">{url}</a> <a href="{change_url}" class="button">Changer l\'URL</a>'
                ' <a href="{clear_url}" class="button">Supprimer l\'URL</a>',
                url=front_url(
                    "person_form_private_submissions", args=(object.result_url_uuid,)
                ),
                change_url=reverse(
                    "admin:people_personform_create_result_url", args=(object.pk,)
                ),
                clear_url=reverse(
                    "admin:people_personform_clear_result_url", args=(object.pk,)
                ),
            )

        return format_html(
            '<em>Pas d\'URL pour le moment</em> <a href="{change_url}" class="button">Créer une URL</a>',
            change_url=reverse(
                "admin:people_personform_create_result_url", args=(object.pk,)
            ),
        )

    result_url.short_description = "Lien vers les résultats accessible sans connexion"
    result_url.help_text = (
        "Ce lien permet d'accéder à l'ensemble des résultats de ce formulaire sans avoir besoin de se connecter."
        " Faites bien attention en le transmettant à des personnes tierces."
    )

    def submissions_number(self, object):
        return object.submissions_number

    submissions_number.short_description = "Nombre de réponses"


@admin.register(PersonFormSubmission, site=admin_site)
class PersonFormSubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ("person",)

    def has_add_permission(self, request):
        return False

    def return_to_form_results(self):
        return HttpResponseRedirect(
            reverse("admin:people_personform_view_results", args=[self.personform.pk])
        )

    def delete_view(self, request, object_id, extra_context=None):
        self.personform = self.get_object(request, unquote(object_id)).form
        return super().delete_view(request, object_id, extra_context)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        self.personform = self.get_object(request, unquote(object_id)).form
        return super().change_view(request, object_id, form_url, extra_context)

    def detail_view(self, request, object_id):
        self.object = self.get_object(request, unquote(object_id))
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
