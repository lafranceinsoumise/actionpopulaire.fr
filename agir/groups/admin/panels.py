from copy import deepcopy
from datetime import timedelta
from functools import partial, update_wrapper

from django.conf import settings
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import Count, Q, QuerySet
from django.db.models.expressions import RawSQL
from django.urls import path
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, escape, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from agir.events.models import Event
from agir.groups import proxys
from agir.lib.admin.filters import (
    CountryListFilter,
    DepartementListFilter,
    RegionListFilter,
    CirconscriptionLegislativeFilter,
)
from agir.lib.admin.panels import CenterOnFranceMixin
from agir.lib.display import display_price
from agir.lib.utils import front_url
from . import actions
from . import views
from .forms import SupportGroupAdminForm
from .. import models
from ..actions.promo_codes import get_promo_codes
from ..models import Membership, SupportGroup
from ...lib.admin.utils import admin_url


class MembershipInline(admin.TabularInline):
    model = models.Membership
    fields = ("person_link", "membership_type", "description")
    readonly_fields = ("person_link", "description")

    def person_link(self, obj):
        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse("admin:people_person_change", args=(obj.person.id,)),
                escape(obj.person),
            )
        )

    person_link.short_description = _("Personne")

    def has_add_permission(self, request, obj=None):
        return False


class ExternalLinkInline(admin.TabularInline):
    extra = 0
    model = models.SupportGroupExternalLink
    fields = ("url", "label")


class GroupHasEventsFilter(admin.SimpleListFilter):
    title = _("Événements organisés dans les 2 mois précédents ou mois à venir")

    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        return (("yes", _("Oui")), ("no", _("Non")))

    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            current_events_count=Count(
                "organized_events",
                filter=Q(
                    organized_events__start_time__range=(
                        timezone.now() - timedelta(days=62),
                        timezone.now() + timedelta(days=31),
                    ),
                    organized_events__visibility=Event.VISIBILITY_PUBLIC,
                ),
            )
        )
        if self.value() == "yes":
            return queryset.exclude(current_events_count=0)
        if self.value() == "no":
            return queryset.filter(current_events_count=0)


class MembersFilter(admin.SimpleListFilter):
    title = "Membres"
    parameter_name = "members"

    def lookups(self, request, model_admin):
        return (("no_members", "Aucun membre"), ("no_referent", "Aucun animateur"))

    def queryset(self, request, queryset):
        if self.value() == "no_members":
            return queryset.filter(members=None)

        if self.value() == "no_referent":
            return queryset.exclude(
                memberships__membership_type=Membership.MEMBERSHIP_TYPE_REFERENT
            )


class TooMuchMembersFilter(admin.SimpleListFilter):
    MEMBERS_LIMIT = models.SupportGroup.MEMBERSHIP_LIMIT

    title = "Groupe d'action avec trop de membres ({} actuellement)".format(
        MEMBERS_LIMIT
    )
    parameter_name = "group with too much members"

    def lookups(self, request, model_admin):
        return (
            (
                "less_than_{}_members".format(self.MEMBERS_LIMIT),
                "Moins de {} membres".format(self.MEMBERS_LIMIT),
            ),
            (
                "more_than_{}_members".format(self.MEMBERS_LIMIT),
                "Plus de {} membres".format(self.MEMBERS_LIMIT),
            ),
        )

    def queryset(self, request, queryset):
        if self.value() == "less_than_{}_members".format(self.MEMBERS_LIMIT):
            return queryset.filter(membership_count__lt=self.MEMBERS_LIMIT)
        if self.value() == "more_than_{}_members".format(self.MEMBERS_LIMIT):
            return queryset.filter(membership_count__gte=self.MEMBERS_LIMIT)


@admin.register(models.SupportGroup)
class SupportGroupAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    form = SupportGroupAdminForm
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
                    "action_buttons",
                    "promo_code",
                    "allocation",
                )
            },
        ),
        (
            _("Informations"),
            {
                "fields": (
                    "type",
                    "subtypes",
                    "description",
                    "allow_html",
                    "image",
                    "tags",
                    "published",
                    "open",
                    "editable",
                )
            },
        ),
        (
            _("Lieu"),
            {
                "fields": (
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
                    "is_private_messaging_enabled",
                )
            },
        ),
        (
            _("Certification"),
            {
                "fields": (
                    "certifiable",
                    "certification_criteria",
                )
            },
        ),
        (
            _("Export des adhésions"),
            {"permission": "people.export_people", "fields": ("export_buttons",)},
        ),
    )
    inlines = (MembershipInline, ExternalLinkInline)
    readonly_fields = (
        "id",
        "link",
        "action_buttons",
        "created",
        "modified",
        "location_departement_id",
        "coordinates_type",
        "promo_code",
        "allocation",
        "certifiable",
        "certification_criteria",
        "export_buttons",
    )
    date_hierarchy = "created"

    list_display = (
        "name",
        "type",
        "published",
        "location_short",
        "membership_count",
        "created",
        "referents",
        "allocation",
    )
    list_filter = (
        "published",
        GroupHasEventsFilter,
        CountryListFilter,
        CirconscriptionLegislativeFilter,
        DepartementListFilter,
        RegionListFilter,
        "coordinates_type",
        MembersFilter,
        "type",
        "subtypes",
        "tags",
        TooMuchMembersFilter,
    )

    search_fields = ("name", "description", "location_city")
    actions = (actions.export_groups, actions.make_published, actions.unpublish)

    def get_fieldsets(self, request, obj=None):
        fieldsets = deepcopy(super().get_fieldsets(request, obj))
        authorized_fieldsets = []
        for key, props in fieldsets:
            permission = props.pop("permission", False)
            if not permission or request.user.has_perm(permission):
                authorized_fieldsets.append((key, props))
        return tuple(authorized_fieldsets)

    def promo_code(self, object):
        if object.pk and object.tags.filter(label=settings.PROMO_CODE_TAG).exists():
            return ", ".join(code for code, _ in get_promo_codes(object))
        else:
            return "-"

    promo_code.short_description = _("Code promo du mois")

    def referents(self, object):
        referents = object.memberships.filter(
            membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT
        ).select_related("person")
        if referents:
            return " / ".join(a.person.email for a in referents)

        return "-"

    referents.short_description = _("Animateur⋅ices")

    def location_short(self, object):
        return _("{zip} {city}, {country}").format(
            zip=object.location_zip,
            city=object.location_city,
            country=object.location_country.name,
        )

    location_short.short_description = _("Lieu")
    location_short.admin_order_field = "location_zip"

    def membership_count(self, object):
        return format_html(
            _('{nb} (<a href="{link}">Ajouter un membre</a>)'),
            nb=object.membership_count,
            link=reverse("admin:groups_supportgroup_add_member", args=(object.pk,)),
        )

    membership_count.short_description = _("Nombre de membres")
    membership_count.admin_order_field = "membership_count"

    def allocation(self, object, show_add_button=False):
        value = display_price(object.allocation) if object.allocation else "-"

        if show_add_button:
            value = format_html(
                '{value} (<a href="{link}">Changer</a>)',
                value=value,
                link=reverse("admin:donations_operation_add")
                + "?group="
                + str(object.pk),
            )

        return value

    allocation.short_description = _("Allocation")
    allocation.admin_order_field = "allocation"

    def link(self, object):
        if object.pk:
            return format_html(
                '<a href="{0}">{0}</a>',
                front_url("view_group", kwargs={"pk": object.pk}),
            )
        else:
            return mark_safe("-")

    link.short_description = _("Page sur le site")

    @admin.display(description="Actions")
    def action_buttons(self, obj):
        if obj._state.adding:
            return mark_safe("-")

        action_buttons = []

        if obj.type == SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE:
            action_buttons.append(
                (
                    admin_url(
                        "admin:groups_supportgroup_maj_membres_boucles_departementales",
                        args=(obj.pk,),
                    ),
                    "Mettre à jour les membres",
                )
            )
        else:
            action_buttons.append(
                (
                    admin_url("admin:groups_supportgroup_add_member", args=(obj.pk,)),
                    "Ajouter un membre",
                )
            )

        action_buttons.append(
            (
                admin_url("admin:donations_operation_add", query={"group": obj.pk}),
                "Changer l'allocation",
            ),
        )

        html = format_html_join(
            " ", '<a class="button" href="{}">{}</a>', action_buttons
        ) + format_html(
            "<div class='help' style='margin: 0; padding: 0;'>"
            "Attention : cliquer sur ces boutons quitte la page et perd vos modifications courantes."
            "</div>"
        )

        return html

    @admin.display(description="Export des membres")
    def export_buttons(self, obj):
        export_buttons = [
            (
                admin_url(
                    "admin:groups_supportgroup_export_memberships",
                    args=(obj.pk, "csv"),
                ),
                "Exporter au format CSV",
            ),
            (
                admin_url(
                    "admin:groups_supportgroup_export_memberships",
                    args=(obj.pk, "xlsx"),
                ),
                "Exporter au format Excel",
            ),
        ]

        return format_html_join(
            " ", '<a class="button" href="{}" download>{}</a>', export_buttons
        )

    def certifiable(self, object):
        if object.is_certified:
            return "Certifié"

        if object.is_certifiable:
            return "Éligible à la certification"

        return "Ce type de groupe n'est pas éligible à la certification"

    certifiable.short_description = _("Statut")

    def certification_criteria(self, object):
        criteria = object.check_certification_criteria()
        label = {
            "gender": "Animation paritaire",
            "activity": "Au moins trois événements dans les deux derniers mois",
            "creation": "Au moins un mois d’existence",
            "members": "Au moins trois membres actifs, animateur·ices et gestionnaires compris",
            "exclusivity": "Les animateur·ices n'animent pas d'autres groupes locaux certifiés",
        }
        html = [
            f"""
              <div class="checkbox-row">
                <input type="checkbox" disabled="" name="cc-{key}" id="id_cc-{key}" {'checked=''' if criteria[key] else ''}>
                <label class="vCheckboxLabel" for="id_cc-{key}">{value}</label>
              </div>
            """
            for key, value in label.items()
            if key in criteria.keys()
        ]
        return format_html("".join(html))

    certification_criteria.short_description = _("Critères")

    def get_queryset(self, request):
        qs: QuerySet = super().get_queryset(request)

        # noinspection SqlResolve
        return qs.annotate(
            membership_count=RawSQL(
                'SELECT COUNT(*) FROM "groups_membership" WHERE "supportgroup_id" = "groups_supportgroup"."id"',
                (),
            ),
            allocation=RawSQL(
                'SELECT SUM(amount) FROM "donations_operation" WHERE "group_id" = "groups_supportgroup"."id"',
                (),
            ),
        )

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.search(search_term)

        use_distinct = False

        return queryset, use_distinct

    def get_urls(self):
        return [
            path(
                "<uuid:pk>/add_member/",
                self.admin_site.admin_view(self.add_member),
                name="{}_{}_add_member".format(
                    self.opts.app_label, self.opts.model_name
                ),
            ),
            path(
                "<uuid:pk>/maj_membres_boucles_departementales/",
                self.admin_site.admin_view(self.maj_membres_boucles_departementales),
                name="{}_{}_maj_membres_boucles_departementales".format(
                    self.opts.app_label, self.opts.model_name
                ),
            ),
            path(
                "<uuid:pk>/export_memberships/<str:as_format>/",
                self.admin_site.admin_view(self.export_memberships),
                name="{}_{}_export_memberships".format(
                    self.opts.app_label, self.opts.model_name
                ),
            ),
        ] + super().get_urls()

    def add_member(self, request, pk):
        return views.add_member(self, request, pk)

    def maj_membres_boucles_departementales(self, request, pk):
        return views.maj_membres_boucles_departementales(self, request, pk)

    def export_memberships(self, request, pk, as_format):
        return views.export_memberships(self, request, pk, as_format)

    def get_changelist_instance(self, request):
        cl = super().get_changelist_instance(request)
        if request.user.has_perm("donations.add_operation"):
            try:
                idx = cl.list_display.index("allocation")
            except ValueError:
                pass
            else:
                cl.list_display[idx] = update_wrapper(
                    partial(self.allocation, show_add_button=True), self.allocation
                )
        return cl

    def save_form(self, request, form, change):
        return form.save(commit=False, request=request)

    class Media:
        # classe Media requise par le CirconscriptionLegislativeFilter, quand bien même elle est vide
        pass


@admin.register(proxys.ThematicGroup)
class ThematicGroupAdmin(SupportGroupAdmin):
    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj) + ("type",)


@admin.register(models.SupportGroupTag)
class SupportGroupTagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SupportGroupSubtype)
class SupportGroupSubtypeAdmin(admin.ModelAdmin):
    search_fields = ("label", "description")
    list_display = ("label", "description", "type", "visibility")
    list_filter = ("type", "visibility")


@admin.register(models.TransferOperation)
class TransfertOperationAdmin(admin.ModelAdmin):
    search_fields = ("former_group", "new_group")
    list_display = ("timestamp", "former_group", "new_group", "members_count")

    fieldsets = (
        (None, {"fields": ("timestamp", "former_group", "new_group", "manager")}),
        ("Personnes concernées", {"fields": ("members_count", "members_list")}),
    )

    readonly_fields = (
        "timestamp",
        "former_group",
        "new_group",
        "manager",
        "members_count",
        "members_list",
    )

    def members_count(self, obj):
        return obj.members.count()

    members_count.short_description = "Nombre de membres concernés"

    def members_list(self, obj):
        return format_html_join(
            mark_safe("<br>"),
            '<a href="{}">{}</a>',
            (
                (reverse("admin:people_person_change", args=(p.id,)), str(p))
                for p in obj.members.all()
            ),
        )

    members_list.short_description = "Liste des membres concernés"
