from django import forms
from django.contrib import admin
from django.db.models import Count, Q

from agir.lib.form_fields import AdminRichEditorWidget
from agir.notifications.models import Notification, NotificationStatus
from agir.api.admin import admin_site


class NotificationForm(forms.ModelForm):
    class Meta:
        fields = ("content", "icon", "link", "start_date", "end_date", "segment")
        widgets = {"content": AdminRichEditorWidget()}


@admin.register(Notification, site=admin_site)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationForm
    fields = (
        "content",
        "icon",
        "link",
        "start_date",
        "end_date",
        "segment",
        "seen",
        "clicked",
    )

    readonly_fields = ("seen", "clicked")

    list_display = ("__str__", "seen", "clicked")

    def get_queryset(self, request):
        return Notification.objects.annotate(
            seen=Count("status"),
            clicked=Count(
                "status", filter=Q(status__status=NotificationStatus.STATUS_CLICKED)
            ),
        )

    def seen(self, notification):
        return notification.seen

    seen.short_description = "Vues"

    def clicked(self, notification):
        return notification.clicked

    clicked.short_description = "Clics"
