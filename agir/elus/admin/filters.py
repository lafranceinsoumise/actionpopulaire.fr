from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Exists, OuterRef
from django.utils import timezone

from agir.elus.models import MandatMunicipal, CHAMPS_ELUS_PARRAINAGES
from agir.lib.autocomplete_filter import AutocompleteFilter, SelectModelFilter


class ConseilFilter(AutocompleteFilter):
    field_name = "conseil"
    title = "Commune d'élection"


class DepartementFilter(SelectModelFilter):
    field_name = "conseil__departement"
    title = "Département"


class DepartementRegionFilter(SelectModelFilter):
    field_name = "conseil__departement__region"
    title = "Région"


class RegionFilter(SelectModelFilter):
    field_name = "conseil__region"
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


class DatesFilter(SimpleListFilter):
    parameter_name = "dates"
    title = "Dates du mandat"

    def lookups(self, request, model_admin):
        return [
            ("O", "Mandats en cours seulement"),
            ("P", "Mandats passés seulement"),
            ("F", "Mandats non commencés seulement"),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == "O":
            return queryset.filter(dates__contains=timezone.now().date())
        elif value == "P":
            return queryset.filter(dates__endswith__lte=timezone.now().date())
        elif value == "F":
            return queryset.filter(dates__startswith__gt=timezone.now().date())
        return queryset


class AppelEluFilter(SimpleListFilter):
    title = "2022 Appel élu⋅es"
    parameter_name = "2022_appel_elus"

    def lookups(self, request, model_admin):
        return (
            ("O", "Signé appel élu"),
            ("N", "Pas signé appel élu"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "O":
            return queryset.exclude(
                person__meta__subscriptions__NSP__mandat__isnull=True
            )
        elif value == "N":
            return queryset.filter(
                person__meta__subscriptions__NSP__mandat__isnull=True
            )
        return queryset


class ReferenceFilter(SimpleListFilter):
    parameter_name = "reference"
    title = "Fiche RNE"

    def lookups(self, request, model_admin):
        return (
            ("O", "Avec fiche RNE"),
            ("N", "Sans fiche RNE"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(reference__isnull=value == "N")
        return queryset


class MandatsFilter(SimpleListFilter):
    parameter_name = "mandats"
    title = "Mandats associés aux fiches"

    def lookups(self, request, model_admin):
        return (
            ("O", "Avec un mandat référencé"),
            ("D", "Avec plus d'un mandat référencé (doublon)"),
            ("N", "Sans mandat référencé"),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == "D":
            return queryset.annotate(n=Count("elu")).filter(n__gt=1)
        elif value in ["O", "N"]:
            return queryset.annotate(
                avec_mandat=Exists(
                    MandatMunicipal.objects.filter(reference_id=OuterRef("id"))
                )
            ).filter(avec_mandat=value == "O")
        return queryset


class TypeEluFilter(SimpleListFilter):
    parameter_name = "type-elu"
    title = "Type d'élu·e"

    def lookups(self, request, model_admin):
        return (
            (f, model_admin.model._meta.get_field(f).verbose_name)
            for f in CHAMPS_ELUS_PARRAINAGES
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value in CHAMPS_ELUS_PARRAINAGES:
            return queryset.filter(**{f"{value}__isnull": False})
        return queryset
