from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agir.elections.models import PollingStationOfficer
from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter


class CommuneListFilter(AutocompleteRelatedModelFilter):
    field_name = "voting_commune"
    title = "commune"


class ConsulateListFilter(AutocompleteRelatedModelFilter):
    field_name = "voting_consulate"
    title = "consulat"


class CirconscriptionLegislativeListFilter(AutocompleteRelatedModelFilter):
    field_name = "voting_circonscription_legislative"
    title = "circonscription législative"


class DepartementListFilter(AutocompleteRelatedModelFilter):
    field_name = "voting_commune__departement"
    title = "département"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(voting_commune__departement=self.value())
                | Q(voting_commune__commune_parent__departement=self.value())
            )

        return queryset


class IsAvailableForVotingDateListFilter(admin.SimpleListFilter):
    title = "date de disponibilité"
    parameter_name = "available_voting_dates"

    def lookups(self, request, model_admin):
        return PollingStationOfficer.VOTING_DATE_CHOICES

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(available_voting_dates__contains=[self.value()])
        return queryset


@admin.register(PollingStationOfficer)
class PollingStationOfficerModelAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "role",
        "commune_consulate",
        "circonscription_legislative",
        "voting_departement",
        "created__date",
        "available_voting_dates",
        "person_link",
    )
    list_filter = (
        "role",
        DepartementListFilter,
        CirconscriptionLegislativeListFilter,
        CommuneListFilter,
        ConsulateListFilter,
        IsAvailableForVotingDateListFilter,
    )
    readonly_fields = (
        "created",
        "circonscription_legislative",
        "voting_departement",
        "departement",
        "polling_station_label",
    )
    autocomplete_fields = (
        "voting_circonscription_legislative",
        "voting_commune",
        "voting_consulate",
        "person",
    )
    search_fields = [
        "contact_email",
        "person__search",
        "voting_circonscription_legislative__code",
        "voting_commune__search",
        "voting_consulate__nom",
        "voting_consulate__search",
    ]
    fieldsets = (
        (
            "Coordonnées",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "birth_name",
                    "gender",
                    "birth_date",
                    "birth_city",
                    "birth_country",
                    "person",
                )
            },
        ),
        (
            "Informations électorales",
            {
                "fields": (
                    "voting_commune",
                    "voting_circonscription_legislative",
                    "voting_departement",
                    "voting_consulate",
                    "polling_station",
                    "polling_station_label",
                    "voter_id",
                )
            },
        ),
        (
            "Disponibilités",
            {"fields": ("role", "has_mobility", "available_voting_dates")},
        ),
        (
            "Contact",
            {"fields": ("contact_email", "contact_phone", "remarks")},
        ),
        (
            "Adresse",
            {
                "fields": (
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "location_country",
                    "departement",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "voting_commune",
                "voting_commune__commune_parent",
                "voting_consulate",
                "person",
            )
        )

    def created__date(self, instance):
        return instance.created.date()

    created__date.short_description = "date de création"
    created__date.admin_order_field = "created"

    def commune_consulate(self, instance):
        if instance.voting_commune is not None:
            return instance.voting_commune
        return instance.voting_consulate

    commune_consulate.short_description = "commune / consulat"

    def polling_station_label(self, instance):
        return instance.polling_station_label

    polling_station_label.short_description = "Libellé du bureau de vote"

    def voting_departement(self, instance):
        if instance.voting_commune is None:
            return "-"

        if instance.voting_commune.commune_parent is not None:
            return instance.voting_commune.commune_parent.departement

        return instance.voting_commune.departement

    voting_departement.short_description = "département"

    def circonscription_legislative(self, instance):
        if instance.voting_circonscription_legislative is not None:
            return instance.voting_circonscription_legislative.code

        return "-"

    circonscription_legislative.short_description = "circonscription législative"

    def person_link(self, instance):
        if instance.person is None:
            return "-"
        href = reverse("admin:people_person_change", args=(instance.person_id,))
        return mark_safe(format_html(f'<a href="{href}">{instance.person}</a>'))

    person_link.short_description = "personne"

    class Media:
        pass
