from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.urls import reverse

from agir.api.admin import admin_site
from agir.municipales.models import CommunePage


class CheffeDeFileFilter(SimpleListFilter):
    title = "Chef⋅fes de fil"
    parameter_name = "cheffes_file"

    def lookups(self, request, model_admin):
        return (
            ("O", "Uniquement les communes avec"),
            ("N", "Uniquement les communes sans"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "O":
            return queryset.exclude(municipales2020_admins=None)
        elif value == "N":
            return queryset.filter(municipales2020_admins=None)
        return queryset


@admin.register(CommunePage, site=admin_site)
class CommunePageAdmin(admin.ModelAdmin):
    readonly_fields = ("code", "code_departement", "name")
    fieldsets = (
        (None, {"fields": readonly_fields}),
        (
            "Informations sur la campagne",
            {
                "fields": (
                    "published",
                    "strategy",
                    "tete_liste",
                    "contact_email",
                    "first_name_1",
                    "last_name_1",
                    "first_name_2",
                    "last_name_2",
                )
            },
        ),
        (
            "Présence de la campagne sur internet",
            {"fields": ("twitter", "facebook", "website")},
        ),
        (
            "Informations pour les dons par chèque",
            {"fields": ("ordre_don", "adresse_don")},
        ),
        ("Permission", {"fields": ("municipales2020_admins",)}),
    )

    list_display = (
        "__str__",
        "published",
        "strategy",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
        "twitter",
        "facebook",
        "website",
    )
    list_editable = (
        "published",
        "strategy",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
    )

    # doit être True-ish pour déclencher l'utilisation
    search_fields = ("name", "code_departement")
    autocomplete_fields = ("municipales2020_admins",)
    list_filter = (CheffeDeFileFilter, "published")

    def get_absolute_url(self):
        return reverse(
            "view_commune",
            kwargs={"code_departement": self.code_departement, "slug": self.slug},
        )

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.search(search_term)

        use_distinct = False
        return queryset, use_distinct

    def has_add_permission(self, request):
        return False
