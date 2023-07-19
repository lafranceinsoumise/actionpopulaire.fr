from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from agir.donations.models import SpendingRequest
from agir.groups.models import SupportGroup
from agir.lib.admin.autocomplete_filter import (
    AutocompleteRelatedModelFilter,
    AutocompleteSelectModelBaseFilter,
)
from agir.lib.admin.filters import DepartementListFilter
from agir.lib.admin.form_fields import AutocompleteSelectModel
from agir.people.models import Person


class MonthlyAllocationSubscriptionPersonFilter(AutocompleteRelatedModelFilter):
    title = "Personne"
    parameter_name = "subscription_person"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.qs_filter_key = "subscription__person_id"

    def get_widget_instance(self):
        return AutocompleteSelectModel(
            Person,
            self.model_admin.admin_site,
        )

    def get_queryset_for_field(self):
        return Person.objects.all()


class MonthlyAllocationGroupFilter(AutocompleteRelatedModelFilter):
    title = "Groupe"
    parameter_name = "group"

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        self.qs_filter_key = "group_id"

    def get_widget_instance(self):
        return AutocompleteSelectModel(
            SupportGroup,
            self.model_admin.admin_site,
        )

    def get_queryset_for_field(self):
        return SupportGroup.objects.all()


class RequestStatusFilter(admin.SimpleListFilter):
    title = _("Statut")

    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("group", _("En attente du groupe")),
            ("review", _("À revoir")),
            ("to_pay", _("À payer")),
            ("finished", _("Terminées")),
        )

    def queryset(self, request, queryset):
        if self.value() == "group":
            return queryset.filter(
                status__in=(
                    SpendingRequest.Status.DRAFT,
                    SpendingRequest.Status.AWAITING_PEER_REVIEW,
                    SpendingRequest.Status.AWAITING_SUPPLEMENTARY_INFORMATION,
                    SpendingRequest.Status.VALIDATED,
                )
            )
        elif self.value() == "review":
            return queryset.filter(status=SpendingRequest.Status.AWAITING_ADMIN_REVIEW)
        elif self.value() == "to_pay":
            return queryset.filter(status=SpendingRequest.Status.TO_PAY)
        elif self.value() == "finished":
            return queryset.filter(
                status__in=(SpendingRequest.Status.PAID, SpendingRequest.Status.REFUSED)
            )
        else:
            return queryset.filter()


class SupportGroupFilter(AutocompleteSelectModelBaseFilter):
    title = "groupe"
    filter_model = SupportGroup
    parameter_name = "group"

    def get_queryset_for_field(self):
        return SupportGroup.objects.all()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(group_id=self.value())
        else:
            return queryset


class DepartementFilter(DepartementListFilter):
    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(departement=self.value())
