from django.contrib import admin
from django.urls import reverse

from agir.api.admin import admin_site
from agir.municipales.models import CommunePage


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
                    "municipale_list_name",
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
        ("Permission", {"fields": ("municipales2020_admins",)}),
    )

    list_display = (
        "__str__",
        "published",
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
        "published",
        "municipale_list_name",
        "first_name_1",
        "last_name_1",
        "first_name_2",
        "last_name_2",
    )

    # doit être True-ish pour déclencher l'utilisation
    search_fields = ("name", "code_departement")
    autocomplete_fields = ("municipales2020_admins",)

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
