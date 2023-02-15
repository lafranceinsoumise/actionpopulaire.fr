from django.contrib import admin
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin as BaseTOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice
from push_notifications.admin import DeviceAdmin
from push_notifications.models import GCMDevice, WNSDevice, APNSDevice

admin.site.unregister(TOTPDevice)

admin.site.unregister(GCMDevice)
admin.site.unregister(WNSDevice)
admin.site.unregister(APNSDevice)


@admin.register(TOTPDevice)
class TOTPDeviceAdmin(BaseTOTPDeviceAdmin):
    list_display = ["email", "name", "confirmed", "qrcode_link"]

    def email(self, obj):
        return obj.user.person.display_email


class PushDeviceAdmin(DeviceAdmin):
    list_display = ("__str__", "device_id", "get_person", "active", "date_created")
    search_fields = ("user__person__search",)

    def get_person(self, device):
        return device.user.person

    get_person.short_description = "Personne"


admin.site.register(APNSDevice, PushDeviceAdmin)
admin.site.register(GCMDevice, PushDeviceAdmin)
