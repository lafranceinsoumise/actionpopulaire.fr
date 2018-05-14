from ajax_select.fields import AutoCompleteSelectField
from django import forms
from django.contrib import admin

from agir.api.admin import admin_site
from . import models


class PaymentForm(forms.ModelForm):
    person = AutoCompleteSelectField(
        "people",
        required=True,
        label="Personne"
    )

    class Meta:
        fields = '__all__'


@admin.register(models.Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentForm
    list_display = ('type', 'person', 'email', 'first_name', 'last_name', 'price', 'status', 'created')
    readonly_fields = ('type', 'person', 'email', 'first_name', 'last_name', 'price', 'status', 'phone_number',
                       'location_address1', 'location_address2', 'location_zip', 'location_city',
                       'location_country', 'meta', 'systempay_responses')
    fields = readonly_fields
    list_filter = ('price', 'status')
    search_fields = ('email', 'person__emails__address')
