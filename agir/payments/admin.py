from django.contrib import admin

from agir.api.admin import admin_site
from . import models


@admin.register(models.Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('type', 'person', 'email', 'first_name', 'last_name', 'price', 'status', 'created')
    readonly_fields = ('type', 'person', 'email', 'first_name', 'last_name', 'price', 'status', 'phone_number',
                       'location_address1', 'location_address2', 'location_zip', 'location_city',
                       'location_country', 'meta', 'systempay_responses')
    fields = readonly_fields
    list_filter = ('price', 'status')
    search_fields = ('email', 'person__emails__address')
