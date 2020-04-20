from django.contrib import admin
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django_otp.plugins.otp_totp.models import TOTPDevice

admin.site.unregister(TOTPDevice)


@admin.register(TOTPDevice)
class DeviceAdmin(TOTPDeviceAdmin):
    list_display = ["email", "name", "confirmed", "qrcode_link"]

    def email(self, obj):
        return obj.user.person.email
