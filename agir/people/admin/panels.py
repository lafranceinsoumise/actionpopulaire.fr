import json
import secrets
from functools import partial
from urllib.parse import urlencode

import django_otp
from django.contrib import admin, messages
from django.contrib.admin.options import IncorrectLookupParameters
from django.contrib.admin.utils import display_for_value, unquote
from django.contrib.admin.views.main import ERROR_FLAG
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.gis.admin import OSMGeoAdmin
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Count, Max, Func, Value, Q
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
from agir.groups.models import SupportGroup, Membership
from agir.lib.admin import (
    DisplayContactPhoneMixin,
    CenterOnFranceMixin,
    DepartementListFilter,
    RegionListFilter,
)
from agir.lib.autocomplete_filter import AutocompleteFilter
from agir.lib.utils import generate_token_params, front_url
from agir.mailing.models import Segment
from agir.people.admin.actions import export_people_to_csv
from agir.people.admin.forms import PersonAdminForm, PersonFormForm
from agir.people.admin.inlines import RSVPInline, MembershipInline, EmailInline
from agir.people.admin.views import (
    FormSubmissionViewsMixin,
    AddPersonEmailView,
    MergePersonsView,
    PersonFormSandboxView,
)
from agir.people.models import Person, PersonTag
from agir.people.person_forms.display import default_person_form_display
from agir.people.person_forms.models import PersonForm, PersonFormSubmission

__all__ = [
    "PersonAdmin",
    "PersonTagAdmin",
    "PersonFormAdmin",
    "PersonFormSubmissionAdmin",
    "ContactAdmin",
]


class SegmentFilter(AutocompleteFilter):
    title = "segment"

    def get_rendered_widget(self):
        rel = models.ForeignKey(to=Segment, on_delete=models.CASCADE)
        rel.model = Segment
        widget = AutocompleteSelect(
            rel,
            self.model_admin.admin_site,
        )
        FieldClass = self.get_form_field()
        field = FieldClass(
            queryset=self.get_queryset_for_field(),
            widget=widget,
            required=False,
        )

        self._add_media(self.model_admin, widget)

        attrs = self.widget_attrs.copy()
        attrs["id"] = "id-%s-autocomplete-filter" % self.field_name
        attrs["class"] = f'{attrs.get("class", "")} select-filter'.strip()

        return field.widget.render(
            name=self.parameter_name,
            value=self.used_parameters.get(self.parameter_name, ""),
            attrs=attrs,
        ) + format_html(
            '<a style="margin-top: 5px" href="{}">Gérer les segments</a>',
            reverse("admin:mailing_segment_changelist"),
        )

    def get_queryset_for_field(self):
        return Segment.objects.all()

    def queryset(self, request, queryset):
        if self.value():
            try:
                s = Segment.objects.get(pk=self.value())
            except Segment.DoesNotExist:
                return queryset
            return queryset.filter(pk__in=s.get_subscribers_queryset())
        else:
            return queryset


class TagListFilter(AutocompleteFilter):
    field_name = "tags"
    title = "Tags"


class AnimateMoreThanOneGroup(admin.SimpleListFilter):
    title = "Cette personne anime plus d'un groupe d'action"
    parameter_name = "Person who animate more than one group"

    def lookups(self, request, model_admin):
        return (
            ("animate_more_than_one_group", "Anime plus d'un groupe"),
            ("", ""),
        )

    def queryset(self, request, queryset):
        if self.value() == "animate_more_than_one_group":
            return queryset.annotate(
                animated_groups=Count(
                    "memberships",
                    filter=Q(
                        memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER
                    ),
                )
            ).filter(animated_groups__gt=1)


@admin.register(Person)
class PersonAdmin(DisplayContactPhoneMixin, CenterOnFranceMixin, OSMGeoAdmin):
    list_display = (
        "__str__",
        "display_contact_phone",
        "is_insoumise",
        "is_2022",
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
                    "subscribed_sms",
                    "campaigns_link",
                )
            },
        ),
        (
            _("Paramètres de participation"),
            {"fields": ("is_insoumise", "is_2022", "draw_participation")},
        ),
        (_("Profil"), {"fields": ("gender", "date_of_birth", "tags", "mandats")}),
        (
            _("Contact et adresse"),
            {
                "fields": (
                    "contact_phone",
                    "location_name",
                    "location_address1",
                    "location_address2",
                    "location_city",
                    "location_zip",
                    "location_state",
                    "location_country",
                    "location_citycode",
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
        "campaigns_link",
        "supportgroups",
        "events",
        "coordinates_type",
        "mandats",
        "location_citycode",
    )

    list_filter = (
        SegmentFilter,
        DepartementListFilter,
        RegionListFilter,
        "is_insoumise",
        "is_2022",
        "subscribed_sms",
        "draw_participation",
        "gender",
        TagListFilter,
        AnimateMoreThanOneGroup,
        ("created", DateRangeFilter),
    )

    inlines = (RSVPInline, MembershipInline, EmailInline)

    autocomplete_fields = ("tags",)

    # doit être non vide pour afficher le formulaire de recherche,
    # mais n'est en réalité pas utilisé pour déterminer les champs
    # de recherche
    search_fields = ["search", "contact_phone"]
    date_hierarchy = "created"

    actions = (export_people_to_csv,)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.search(search_term)

        use_distinct = False

        return queryset, use_distinct

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("emails")

    def role_link(self, obj):
        if obj.role is not None:
            return format_html(
                '<a href="{link}">{text}</a>',
                link=reverse("admin:authentication_role_change", args=[obj.role_id]),
                text=_("Voir le rôle"),
            )
        return "Pas de compte associé à cette personne"

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

    def campaigns_link(self, obj):
        return format_html(
            '<a href="{}" class="button">Voir l\'historique</a>',
            reverse("admin:nuntius_campaignsentevent_changelist")
            + "?subscriber_id__exact="
            + str(obj.pk),
        )

    campaigns_link.short_description = "Campagnes envoyées"

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

        chart_data = (
            cl.get_queryset(request)
            .exclude(meta__subscriptions__NSP__date__isnull=True)
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
        }

        return TemplateResponse(
            request,
            "admin/people/person/statistics.html",
            context,
        )

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj) or (
            request.resolver_match.url_name == "people_person_autocomplete"
            and request.user.has_perm("people.select_person")
        )

    def has_export_permission(self, request):
        return request.user.has_perm("people.export_people")

    def changelist_view(self, request, extra_context=None):
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
                    "segment",
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
                    "campaign_template",
                )
            },
        ),
        (_("Champs"), {"fields": ("main_question", "tags", "custom_fields", "config")}),
        (
            _("Textes"),
            {
                "fields": (
                    "short_description",
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
    autocomplete_fields = ("required_tags", "segment", "tags", "campaign_template")

    def last_submission(self, obj):
        last_submission = obj.submissions.last()
        if last_submission is None:
            return mark_safe("-")
        return last_submission.created

    last_submission.short_description = "Dernière réponse"
    last_submission.admin_order_field = "last_submission"

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
            path(
                "sandbox/",
                self.admin_site.admin_view(
                    PersonFormSandboxView.as_view(model_admin=self)
                ),
                name="people_personform_sandbox",
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


@admin.register(PersonFormSubmission)
class PersonFormSubmissionAdmin(admin.ModelAdmin):
    autocomplete_fields = ("person",)

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


class Contact(Person):
    class Meta:
        proxy = True


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_address",
        "is_liaison",
        "is_2022",
        "created",
        "subscriber",
    )
    list_filter = (
        SegmentFilter,
        "is_2022",
        ("created", DateRangeFilter),
    )

    # doit être non vide pour afficher le formulaire de recherche,
    # mais n'est en réalité pas utilisé pour déterminer les champs
    # de recherche
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
        return obj.NEWSLETTER_2022_LIAISON in obj.newsletters

    is_liaison.short_description = "Correspondant·e d'immeuble"
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
            super(ContactAdmin, self)
            .get_queryset(*args, **kwargs)
            .filter(meta__subscriptions__AP__subscriber__isnull=False)
        )

    class Media:
        pass
