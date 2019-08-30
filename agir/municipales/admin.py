from django.contrib import admin

from agir.api.admin import admin_site
from agir.municipales.models import CommunePage


@admin.register(CommunePage, site=admin_site)
class CommunePageAdmin(admin.ModelAdmin):
    readonly_fields = ("code", "code_departement", "name")
    fields = readonly_fields + ("twitter",)
    list_display = ("__str__",)
    search_fields = ("name",)

    def has_add_permission(self, request):
        return False
