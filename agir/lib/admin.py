from typing import Iterable

import django_countries
from django.contrib import admin
from django.contrib.admin import helpers
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from agir.lib import data
from agir.lib.data import FRANCE_COUNTRY_CODES


class CenterOnFranceMixin:
    # for some reason it has to be in projected coordinates
    default_lon = 364043
    default_lat = 5850840
    default_zoom = 5


class DisplayContactPhoneMixin:
    def display_contact_phone(self, object):
        if object.contact_phone:
            return object.contact_phone.as_international
        return "-"

    display_contact_phone.short_description = _("Numéro de contact")
    display_contact_phone.admin_order_field = "contact_phone"


class CountryListFilter(admin.SimpleListFilter):
    title = "Pays"
    parameter_name = "location_country"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return [
            ("FR_all", "France (outremer compris)"),
            ("not_FR_all", "Hors France (outremer compris)"),
        ] + list(django_countries.countries)

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        if self.value() == "FR_all":
            return queryset.filter(location_country__in=FRANCE_COUNTRY_CODES)
        if self.value() == "not_FR_all":
            return queryset.exclude(location_country__in=FRANCE_COUNTRY_CODES)
        else:
            return queryset.filter(location_country=self.value())


class DepartementListFilter(admin.SimpleListFilter):
    title = "Département"
    parameter_name = "departement"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return data.departements_choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(data.filtre_departement(self.value()))


class RegionListFilter(admin.SimpleListFilter):
    title = "Région"
    parameter_name = "region"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return data.regions_choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(data.filtre_region(self.value()))


class AdminViewMixin:
    def get_admin_helpers(self, form, fields: Iterable[str] = None, fieldsets=None):
        if fieldsets is None:
            fieldsets = [(None, {"fields": list(fields)})]

        admin_form = helpers.AdminForm(
            form=form,
            fieldsets=fieldsets,
            model_admin=self.kwargs["model_admin"],
            prepopulated_fields={},
        )

        return {
            "adminform": admin_form,
            "errors": helpers.AdminErrorList(form, []),
            "media": self.kwargs["model_admin"].media + admin_form.media,
        }

    def get_context_data(self, **kwargs):
        model_admin = self.kwargs["model_admin"]

        kwargs.setdefault("opts", model_admin.model._meta)
        kwargs.setdefault("add", False)
        kwargs.setdefault("change", False)
        kwargs.setdefault("is_popup", False)
        kwargs.setdefault("save_as", False)
        kwargs.setdefault(
            "has_add_permission", model_admin.has_add_permission(self.request)
        )
        kwargs.setdefault(
            "has_change_permission", model_admin.has_change_permission(self.request)
        )
        kwargs.setdefault(
            "has_view_permission", model_admin.has_view_permission(self.request)
        )
        kwargs.setdefault("has_editable_inline_admin_formsets", False)
        kwargs.setdefault("has_delete_permission", False)
        kwargs.setdefault("show_close", False)

        return super().get_context_data(**kwargs)


class PersonLinkMixin:
    def person_link(self, obj):
        if obj.person is not None:
            return mark_safe(
                '<a href="%s">%s</a>'
                % (
                    reverse("admin:people_person_change", args=(obj.person.id,)),
                    escape(obj.person),
                )
            )

        return "Aucune"

    person_link.short_description = "Personne"
