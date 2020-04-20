from django.contrib.admin import SimpleListFilter

from agir.elus.models import MandatMunicipal
from agir.lib.autocomplete_filter import AutocompleteFilter, SelectModelFilter


class CommuneFilter(AutocompleteFilter):
    field_name = "commune"
    title = "Commune d'élection"


class DepartementFilter(SelectModelFilter):
    field_name = "commune__departement"
    title = "Département"


class RegionFilter(SelectModelFilter):
    field_name = "commune__departement__region"
    title = "Région"


class CommunautaireFilter(SimpleListFilter):
    parameter_name = "communautaire"
    title = "Par type de mandat communautaire"

    def lookups(self, request, model_admin):
        return [
            *MandatMunicipal.MANDAT_EPCI_CHOICES,
            ("AVEC", "Tous les mandats communautaire"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "AVEC":
            return queryset.exclude(
                communautaire=MandatMunicipal.MANDAT_EPCI_PAS_DE_MANDAT
            )
        elif self.value() in {v for v, l in MandatMunicipal.MANDAT_EPCI_CHOICES}:
            return queryset.filter(communautaire=self.value())
        return queryset
