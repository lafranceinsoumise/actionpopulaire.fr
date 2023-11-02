from data_france.models import CirconscriptionLegislative
from django.contrib import admin
from django.db.models import Subquery, Q

from agir.lib import data
from agir.lib.admin.autocomplete_filter import (
    AutocompleteSelectModelBaseFilter,
    AutocompleteRelatedModelFilter,
)


class DepartementListFilter(admin.SimpleListFilter):
    title = "département"
    parameter_name = "commune__departement__code"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return data.departements_choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(commune__departement__code=self.value())


class RegionListFilter(admin.SimpleListFilter):
    title = "région"
    parameter_name = "commune__departement__region__code"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return data.regions_choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset

        return queryset.filter(commune__departement__region__code=self.value())


class CirconscriptionLegislativeFilter(AutocompleteSelectModelBaseFilter):
    title = "circonscription législative"
    filter_model = CirconscriptionLegislative
    parameter_name = "circonscription_legislative"

    def get_queryset_for_field(self):
        return CirconscriptionLegislative.objects.exclude(geometry__isnull=True)

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        return queryset.exclude(commune__mairie_localisation__isnull=True).filter(
            commune__mairie_localisation__intersects=Subquery(
                CirconscriptionLegislative.objects.filter(pk=self.value()).values(
                    "geometry"
                )[:1]
            )
        )


class CommuneListFilter(AutocompleteRelatedModelFilter):
    field_name = "commune"
    title = "commune"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(commune=self.value()) | Q(commune__commune_parent=self.value())
            )
        else:
            return queryset
