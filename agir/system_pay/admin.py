from django.contrib import admin

from agir.api.admin import admin_site
from . import models


@admin.register(models.SystemPayTransaction, site=admin_site)
class SystemPayTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'person', 'status', 'webhook_calls')
    readonly_fields = ('id', 'payment', 'person', 'status', 'webhook_calls')
    fields = readonly_fields
    list_filter = ('status',)
    search_fields = ('payment__email', 'payment__person__emails__address')

    def person(self, obj):
        return obj.payment.person
