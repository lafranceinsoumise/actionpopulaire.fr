from django import forms
from django.contrib import admin
from django.db import transaction
from django.utils import timezone

from agir.api.admin import admin_site
from agir.payments.actions import notify_status_change
from agir.payments.models import Payment
from agir.payments.payment_modes import PaymentModeField
from . import models


class PaymentAdminForm(forms.ModelForm):
    mode = PaymentModeField(required=True)

    def clean_mode(self):
        mode = self.cleaned_data['mode']
        print(mode, flush=True)
        if not mode.can_admin:
            raise forms.ValidationError("Seuls peuvent être modifiés les paiements par chèque.")

        return mode

    def clean_status(self):
        if self.instance.status != Payment.STATUS_WAITING:
            raise forms.ValidationError("Seuls peuvent être modifiés les paiements en attente.")

        return self.cleaned_data['status']

    def save(self, *args, **kwargs):
        with transaction.atomic():
            notify_status_change(self.instance)
            now = timezone.now().astimezone(timezone.utc).isoformat()
            self.instance.events.append(
                {'change_status': self.instance.status, 'date': now, 'origin': 'check_payment_admin_change_button'}
            )

            return super().save(*args, **kwargs)

    class Meta:
        model = Payment
        fields = ('type', 'person', 'email', 'first_name', 'last_name', 'price', 'phone_number',
                       'location_address1', 'location_address2', 'location_zip', 'location_city',
                       'location_country', 'meta', 'events', 'status', 'mode')


@admin.register(models.Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentAdminForm
    list_display = ('type', 'person', 'email', 'first_name', 'last_name', 'price', 'status', 'created', 'mode')
    readonly_fields = ('type', 'person', 'email', 'first_name', 'last_name', 'price', 'phone_number',
                       'location_address1', 'location_address2', 'location_zip', 'location_city',
                       'location_country', 'meta', 'events')
    fields = readonly_fields + ('mode', 'status')
    list_filter = ('price', 'status')
    search_fields = ('email', 'person__emails__address')
