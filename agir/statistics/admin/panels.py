from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from agir.statistics import models


@admin.register(models.AbsoluteStatistics)
class AbsoluteStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "event_count",
        "local_supportgroup_count",
        "local_certified_supportgroup_count",
        "membership_person_count",
        "boucle_departementale_membership_person_count",
        "political_support_person_count",
        "lfi_newsletter_subscriber_count",
        "sent_campaign_count",
        "sent_campaign_email_count",
        "created",
        "modified",
    )
    list_filter = (
        ("date", admin.DateFieldListFilter),
        ("date", DateRangeFilter),
    )
    date_hierarchy = "date"
    list_per_page = 15
    show_full_result_count = False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.MaterielStatistics)
class MaterielStatisticsAdmin(admin.ModelAdmin):
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
    list_filter = (
        ("date", admin.DateFieldListFilter),
        ("date", DateRangeFilter),
    )
    date_hierarchy = "date"
    list_per_page = 15
    show_full_result_count = False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
