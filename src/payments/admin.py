from django.contrib import admin

from api.admin import admin_site
from payments import models


@admin.register(models.Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('person', 'email', 'first_name', 'last_name', 'price', 'status')
