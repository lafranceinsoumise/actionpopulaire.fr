from django import forms
from django.contrib import admin

from agir.lib.form_fields import AdminRichEditorWidget
from agir.notifications.models import Notification
from agir.api.admin import admin_site


class NotificationForm(forms.ModelForm):
    class Meta:
        fields = ("content", "icon", "link", "start_date", "end_date", "segment")
        widgets = {"content": AdminRichEditorWidget()}


@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationForm
    fields = ("content", "icon", "link", "start_date", "end_date", "segment")
