import django_countries
from data_france.models import CirconscriptionLegislative, Commune
from django.contrib import admin
from django.db.models import Subquery

from agir.lib import data
from agir.lib.admin.autocomplete_filter import AutocompleteSelectModelBaseFilter
from agir.lib.data import FRANCE_COUNTRY_CODES
from agir.people.models import Person
from agir.statistics.utils import get_commune_queryset, get_commune_filter


class CountryListFilter(admin.SimpleListFilter):
    title = "Pays"
    parameter_name = "location_country"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return [
            ("FR_all", "France (outremer compris)"),
            ("not_FR_all", "Hors France (outremer compris)"),
        ] + list(django_countries.countries)

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        if self.value() == "FR_all":
            return queryset.filter(location_country__in=FRANCE_COUNTRY_CODES)
        if self.value() == "not_FR_all":
            return queryset.exclude(location_country__in=FRANCE_COUNTRY_CODES)
        else:
            return queryset.filter(location_country=self.value())


class DepartementListFilter(admin.SimpleListFilter):
    title = "Département"
    parameter_name = "departement"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return data.departements_choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(data.filtre_departement(self.value()))


class RegionListFilter(admin.SimpleListFilter):
    title = "Région"
    parameter_name = "region"
    template = "admin/dropdown_filter.html"

    def lookups(self, request, model_admin):
        return data.regions_choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(data.filtre_region(self.value()))


class CirconscriptionLegislativeFilter(AutocompleteSelectModelBaseFilter):
    title = "circonscription législative"
    filter_model = CirconscriptionLegislative
    parameter_name = "circo"

    def get_queryset_for_field(self):
        return CirconscriptionLegislative.objects.exclude(geometry__isnull=True)

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                coordinates__intersects=Subquery(
                    CirconscriptionLegislative.objects.filter(pk=self.value()).values(
                        "geometry"
                    )[:1]
                )
            )
        else:
            return queryset


class ParticipantFilter(AutocompleteSelectModelBaseFilter):
    title = "participant·e"
    filter_model = Person
    parameter_name = "participant_id"

    def get_queryset_for_field(self):
        return Person.objects.all()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(rsvps__person_id=self.value())
        else:
            return queryset
