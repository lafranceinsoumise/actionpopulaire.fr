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


class DepartementListFilter(admin.SimpleListFilter):
    title = "Département"
    parameter_name = "departement"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return (
            (departement["id"], departement["nom"]) for departement in data.departements
        )

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(
            location_zip__startswith=self.value().replace("A", "0").replace("B", "0")
        )
