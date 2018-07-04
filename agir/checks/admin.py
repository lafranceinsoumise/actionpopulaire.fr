from django.contrib import admin
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from agir.api.admin import admin_site
from agir.payments.actions import notify_status_change

from .models import CheckPayment


def change_payment_status(status, description):
    def action(modeladmin, request, queryset):
        with transaction.atomic():
            now = timezone.now().astimezone(timezone.utc).isoformat()

            for payment in queryset.filter(status=CheckPayment.STATUS_WAITING):
                payment.status = status
                payment.events.append(
                    {'change_status': status, 'date': now, 'origin': 'check_payment_model_admin'}
                )
                payment.save()
                notify_status_change(payment)
    # have to change the function name so that django admin see that they are different functions
    action.__name__ = f'change_to_{status}'
    action.short_description = description

    return action


@admin.register(CheckPayment, site=admin_site)
class CheckPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'status', 'price', 'person', 'email', 'first_name', 'last_name',)
    fields = readonly_fields = (
        'type', 'mode', 'person', 'email', 'first_name', 'last_name', 'price', 'status', 'phone_number',
        'location_address1', 'location_address2', 'location_zip', 'location_city', 'location_country', 'meta', 'events'
    )

    list_filter = ('price', 'status',)
    search_fields = ('id', 'email', 'first_name', 'last_name')

    actions = [
        change_payment_status(CheckPayment.STATUS_COMPLETED, _('Marquer comme reçu')),
        change_payment_status(CheckPayment.STATUS_CANCELED, _("Marqué comme abandonné par l'acheteur")),
        change_payment_status(CheckPayment.STATUS_REFUSED, _("Marqué comme refusé")),
    ]

    def has_add_permission(self, request):
        """Forbidden to add CheckPayment through this model admin"""
        return False
