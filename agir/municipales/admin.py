from django.contrib import admin
from django.urls import reverse

from agir.api.admin import admin_site
from agir.municipales.models import CommunePage


@admin.register(CommunePage, site=admin_site)
class CommunePageAdmin(admin.ModelAdmin):
    readonly_fields = ("code", "code_departement", "name")
    fields = readonly_fields + (
        "municipale_list_name",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
        "twitter",
        "facebook",
        "website",
        "municipales2020_admins",
    )
    list_display = (
        "__str__",
        "municipale_list_name",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
        "twitter",
        "facebook",
        "website",
    )
    list_editable = (
        "municipale_list_name",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
        "twitter",
        "facebook",
        "website",
    )
    search_fields = ("name",)
    autocomplete_fields = ("municipales2020_admins",)

    def get_absolute_url(self):
        return reverse(
            "view_commune",
            kwargs={"code_departement": self.code_departement, "slug": self.slug},
        )

    def has_add_permission(self, request):
        return False
