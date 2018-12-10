from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from agir.lib import data


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


class ZoneListFilter(admin.SimpleListFilter):
    zone_choices = None
    filter_func = None

    def lookups(self, request, model_admin):
        return self.zone_choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(self.filter_func())


class DepartementListFilter(ZoneListFilter):
    title = "Département"
    parameter_name = "departement"
    template = "admin/dropdown_filter.html"
    zone_choices = data.departements_choices

    def filter_func(self):
        return data.filtre_departement(self.value())


class RegionListFilter(ZoneListFilter):
    title = "Région"
    parameter_name = "region"
    template = "admin/dropdown_filter.html"
    zone_choices = data.regions_choices

    def filter_func(self):
        return data.filtre_region(self.value())
