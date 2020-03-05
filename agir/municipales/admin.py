from django.utils.html import format_html
from functools import reduce

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.urls import reverse
from operator import or_

from agir.api.admin import admin_site
from agir.municipales.models import CommunePage, Liste


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
                    "mandataire_email",
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


class AvecCommuneFilter(SimpleListFilter):
    title = "Avec ou sans commune"
    parameter_name = "avec_commune"

    def lookups(self, request, model_admin):
        return (("O", "Avec commune"), ("N", "Sans commune"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "O":
            return queryset.exclude(commune=None)
        elif value == "N":
            return queryset.filter(commune=None)
        return queryset


class MetropoleOutremerFilter(SimpleListFilter):
    title = "Métropole ou Outremer"
    parameter_name = "metropole_outremer"
    condition = reduce(or_, (Q(code__startswith=str(i)) for i in range(10)))

    def lookups(self, request, model_admin):
        return (("M", "Métropole seulement"), ("O", "Outremer seulement"))

    def queryset(self, request, queryset):
        value = self.value()
        if value == "M":
            return queryset.filter(self.condition)
        elif value == "O":
            return queryset.exclude(self.condition)
        return queryset


@admin.register(Liste, site=admin_site)
class ListeAdmin(admin.ModelAdmin):
    readonly_fields = ("code", "nom", "lien_commune", "nuance", "candidats")

    list_display = ["nom", "lien_commune", "soutien", "nuance"]
    fields = ["code", "nom", "lien_commune", "soutien", "nuance", "candidats"]

    list_filter = ("nuance", "soutien", AvecCommuneFilter, MetropoleOutremerFilter)

    search_fields = ("nom", "code", "commune__name")

    def lien_commune(self, object):
        commune = object.commune
        if commune:
            return format_html(
                '<a href="{link}">{name}</a>',
                link=reverse(
                    "admin:municipales_communepage_change", args=(commune.id,)
                ),
                name=str(commune),
            )

    lien_commune.short_description = "Commune"
