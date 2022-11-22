from django.contrib import admin

from agir.cagnottes.actions import montant_cagnotte
from agir.cagnottes.models import Cagnotte
from agir.lib.display import display_price


@admin.register(Cagnotte)
class CagnotteAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug", "public")
    fieldsets = (
        (None, {"fields": ("nom", "slug", "public", "url_remerciement", "compteur")}),
        ("Présentation", {"fields": ("titre", "legal", "description")}),
    )
    readonly_fields = ("compteur",)

    @admin.display(description="Montant donné")
    def compteur(self, obj):
        return display_price(montant_cagnotte(obj))
