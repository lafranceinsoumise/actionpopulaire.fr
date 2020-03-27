from django.contrib import admin
from django.utils import timezone

from agir.api.admin import admin_site
from agir.elus.models import MandatMunicipal


@admin.register(MandatMunicipal, site=admin_site)
class MandatMunicipalAdmin(admin.ModelAdmin):
    fields = (
        "person",
        "commune",
        "debut",
        "fin",
        "mandat",
        "delegations_municipales",
        "communautaire",
    )

    list_display = ("commune", "person", "mandat", "actif", "communautaire")
    readonly_fields = ("actif",)
    autocomplete_fields = ("person", "commune")

    def actif(self, obj):
        return obj.debut <= timezone.now() <= obj.fin

    actif.short_description = "Actif"
