from ajax_select.fields import AutoCompleteSelectField
from django import forms
from django.contrib import admin

from api.admin import admin_site
from payments import models


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
    list_display = ('person', 'email', 'first_name', 'last_name', 'price', 'status', )
    readonly_fields = ('person', 'email', 'first_name', 'last_name', 'price', 'status')
    list_filter = ('price', 'status')
