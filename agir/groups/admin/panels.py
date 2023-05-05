from copy import deepcopy
from functools import partial, update_wrapper

from django.conf import settings
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import QuerySet
from django.db.models.expressions import RawSQL
from django.http import HttpResponseRedirect
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html, escape, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

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
from . import filters
from . import inlines
from . import views
from .forms import SupportGroupAdminForm
from .. import models
from ..actions.promo_codes import get_promo_codes
from ..models import SupportGroup
from ..utils.certification import (
    check_certification_criteria,
)
from ...lib.admin.utils import admin_url


@admin.register(models.SupportGroup)
class SupportGroupAdmin(VersionAdmin, CenterOnFranceMixin, OSMGeoAdmin):
    history_latest_first = True
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
                    "certification_status",
                    "certification_criteria",
                    "certification_actions",
                )
            },
        ),
        (
            _("Export des adhésions"),
            {"permission": "people.export_people", "fields": ("export_buttons",)},
        ),
    )
    inlines = (inlines.MembershipInline, inlines.ExternalLinkInline)
    readonly_fields = (
        "id",
        "link",
        "action_buttons",
        "created",
        "creation_date",
        "modified",
        "location_departement_id",
        "coordinates_type",
        "promo_code",
        "allocation",
        "is_certified",
        "certification_status",
        "certification_criteria",
        "certification_actions",
        "export_buttons",
    )
    date_hierarchy = "created"

    list_display = (
        "name",
        "type",
        "published",
        "is_certified",
        "location_short",
        "membership_count",
        "creation_date",
        "referents",
        "allocation",
    )
    list_filter = (
        "published",
        filters.CertifiedSupportGroupFilter,
        filters.GroupHasEventsFilter,
        CountryListFilter,
        CirconscriptionLegislativeFilter,
        DepartementListFilter,
        RegionListFilter,
        "coordinates_type",
        filters.MembersFilter,
        "type",
        "subtypes",
        "tags",
        filters.TooMuchMembersFilter,
    )

    search_fields = ("name", "description", "location_city")
    actions = (
        actions.export_groups,
        actions.make_published,
        actions.unpublish,
        actions.certify_supportgroups,
        actions.uncertify_supportgroups,
    )

    def promo_code(self, object):
        if (
            not object.pk
            or not object.tags.filter(label=settings.PROMO_CODE_TAG).exists()
        ):
            return "-"
        codes = []
        for code_data in get_promo_codes(object):
            code = code_data.get("code")
            expiration = code_data.get("expiration").strftime("%d/%m/%Y")
            label = code_data.get("label", "").title()
            code_string = f"<code>{code}</code> — exp. {expiration}"
            if code_data.get("label"):
                code_string += f" ({label})"
            codes.append((mark_safe(code_string),))

        return format_html_join("", "<p>{}</p>", codes)

    promo_code.short_description = _("Code promo en cours")

    def referents(self, obj):
        referents = obj.referents

        if not referents:
            return "-"

        return mark_safe(
            "<br/>".join(
                [
                    '<a style="white-space: nowrap;" href="%s" title="%s">%s %s</a>'
                    % (
                        reverse("admin:people_person_change", args=(person.id,)),
                        escape(person.display_name),
                        escape(person.email),
                        f"({person.gender})" if person.gender else "",
                    )
                    for person in referents
                ]
            )
        )

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
        if obj._state.adding or not obj.memberships.exists():
            return "Ce groupe n'a pas encore de membres"

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

    @admin.display(description="Création", ordering="created")
    def creation_date(self, obj):
        return obj.created.strftime("%d/%m/%Y")

    @admin.display(description="Certifié", boolean=True, ordering="certification_date")
    def is_certified(self, obj):
        return obj.is_certified

    @admin.display(description="Statut")
    def certification_status(self, obj):
        if obj.is_certified:
            status = f"Certifié depuis le {obj.certification_date.strftime('%d %B %Y')}"
            if obj.uncertifiable_warning_date:
                status = mark_safe(
                    f"{status}"
                    "<br />"
                    f"— <em>Avertissement de décertification envoyé "
                    f"le {obj.uncertifiable_warning_date.strftime('%d %B %Y')}</em>"
                )
            return status

        if obj.is_certifiable:
            return "Éligible à la certification"

        return "Ce type de groupe n'est pas éligible à la certification"

    @admin.display(description="Critères")
    def certification_criteria(self, obj):
        acceptable_event_subtype_link = admin_url(
            "admin:events_eventsubtype_changelist",
            query={"is_acceptable_for_group_certification__exact": 1},
        )
        criteria = check_certification_criteria(obj, with_labels=True)
        html = [
            f"""
            <div class="form-row">
              <div class="checkbox-row">
                <input type="checkbox" disabled="" name="cc-{key}" id="id_cc-{key}" {'checked=''' if criterion["value"] else ''}>
                <label class="vCheckboxLabel" for="id_cc-{key}">{criterion["label"]}</label>
                <div class="help">
                  {criterion["help"]}
                  {f' (<a href="{acceptable_event_subtype_link}">'
                    "voir la liste des types d'événement acceptés"
                    "</a>)" if key =='activity' else ""}
                </div>
              </div>
            </div>
            """
            for key, criterion in criteria.items()
        ]
        return format_html("".join(html))

    @admin.display(description="Actions")
    def certification_actions(self, obj):
        certification_actions = []
        if obj and not obj.is_certified:
            certification_actions.append(
                mark_safe(
                    "<input "
                    "type='submit' "
                    "name='_certify' "
                    "style='border-radius:0;background:#078080;' "
                    "value='✔ Certifier le groupe' />"
                )
            )
        if obj and obj.is_certified:
            certification_actions.append(
                mark_safe(
                    "<input "
                    "type='submit' "
                    "name='_uncertify' "
                    "style='border-radius:0;background:#f45d48;' "
                    "value='✖ Décertifier le groupe' />"
                )
            )
        if certification_actions:
            return format_html(
                "<form style='margin: .5rem 0; padding: 0;'>{}</form>",
                mark_safe("<br />".join(certification_actions)),
            )
        return "-"

    def response_change(self, request, obj):
        if "_certify" in request.POST:
            qs = self.model.objects.filter(pk=obj.pk)
            actions.certify_supportgroups(self, request, qs)
            return HttpResponseRedirect(".")

        if "_uncertify" in request.POST:
            qs = self.model.objects.filter(pk=obj.pk)
            actions.uncertify_supportgroups(self, request, qs)
            return HttpResponseRedirect(".")

        return super().response_change(request, obj)

    def get_fieldsets(self, request, obj=None):
        fieldsets = deepcopy(super().get_fieldsets(request, obj))
        authorized_fieldsets = []
        for key, props in fieldsets:
            permission = props.pop("permission", False)
            if not permission or request.user.has_perm(permission):
                authorized_fieldsets.append((key, props))
        return tuple(authorized_fieldsets)

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


@admin.register(proxys.UncertifiableGroup)
class UncertifiableGroupAdmin(SupportGroupAdmin):
    list_display_links = None
    list_display = (
        "group_link",
        "location_short",
        "created__date",
        "active_member_count",
        "referents",
        "recent_event_count",
        "short_certification_criteria",
    )
    list_filter = (
        CountryListFilter,
        CirconscriptionLegislativeFilter,
        DepartementListFilter,
        RegionListFilter,
    )
    date_hierarchy = None
    show_full_result_count = False

    @admin.display(description="Groupe", ordering="name")
    def group_link(self, obj):
        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse("admin:groups_supportgroup_change", args=(obj.id,)),
                escape(obj.name),
            )
        )

    @admin.display(description="Création", ordering="created")
    def created__date(self, obj):
        return obj.created.date()

    @admin.display(description="Membres")
    def active_member_count(self, obj):
        return obj.active_member_count

    @admin.display(description="Actions")
    def recent_event_count(self, obj):
        return obj.recent_event_count

    @admin.display(description="Critères")
    def short_certification_criteria(self, obj):
        criteria = check_certification_criteria(obj, with_labels=True)
        html = [
            f"""
            <div style="white-space: nowrap;" title={criterion["help"]}>
              <img src="/static/admin/img/icon-{'yes' if criterion["value"] else 'no'}.svg" alt="{criterion["value"]}">
              &nbsp;{criterion["label"]}
            </div>
            """
            for key, criterion in criteria.items()
        ]
        return format_html("".join(html))


@admin.register(models.SupportGroupTag)
class SupportGroupTagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SupportGroupSubtype)
class SupportGroupSubtypeAdmin(VersionAdmin):
    history_latest_first = True
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
