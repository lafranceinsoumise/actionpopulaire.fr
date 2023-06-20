from django.contrib import admin
from django.utils.formats import date_format
from rangefilter.filters import DateRangeFilter

from agir.statistics import models


class StatisticsModelAdmin(admin.ModelAdmin):
    change_list_template = "admin/statistics_change_list.html"
    list_filter = (
        ("date", admin.DateFieldListFilter),
        ("date", DateRangeFilter),
    )
    date_hierarchy = "date"
    list_per_page = 15
    show_full_result_count = False
    relative_aggregates = False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        try:
            aggregates = qs.aggregate_for_period()
        except AttributeError:
            return response

        start, end = aggregates.pop("period")
        if start and end:
            response.context_data[
                "period"
            ] = f"du {date_format(start)} au {date_format(end)}"
        else:
            response.context_data["period"] = "Inconnue"
        response.context_data["aggregates"] = {}

        for key, value in aggregates.items():
            if self.model._meta.get_field(key):
                unit = ""
                if (
                    hasattr(self.model, "CURRENCY_FIELDS")
                    and key in self.model.CURRENCY_FIELDS
                ):
                    value = round(value / 100)
                    unit = " €"
                key = self.model._meta.get_field(key).verbose_name
                if self.relative_aggregates:
                    value = f"{value : >+n}{unit}"
                else:
                    value = f"{value : >n}{unit}"
                response.context_data["aggregates"][key] = value

        return response


@admin.register(models.AbsoluteStatistics)
class AbsoluteStatisticsAdmin(StatisticsModelAdmin):
    relative_aggregates = True
    list_display = (
        "date",
        "event_count",
        "local_supportgroup_count",
        "local_certified_supportgroup_count",
        "membership_person_count",
        "boucle_departementale_membership_person_count",
        "political_support_person_count",
        "liaison_count",
        "lfi_newsletter_subscriber_count",
        "sent_campaign_count",
        "sent_campaign_email_count",
        "created",
        "modified",
    )


@admin.register(models.MaterielStatistics)
class MaterielStatisticsAdmin(StatisticsModelAdmin):
    list_display = (
        "date",
        "total_orders",
        "total_items",
        "total_sales",
        "net_sales",
        "average_sales",
        "total_tax",
        "total_shipping",
        "total_refunds",
        "total_discount",
        "created",
        "modified",
    )
