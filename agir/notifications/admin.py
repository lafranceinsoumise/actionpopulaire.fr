from django.contrib import admin

from agir.notifications.models import Notification
from agir.api.admin import admin_site


@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    fields = ("content", "link", "start_date", "end_date", "segment")
