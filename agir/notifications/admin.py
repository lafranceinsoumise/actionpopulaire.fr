from django import forms
from django.contrib import admin
from django.db.models import Count, Q
from django.template.defaultfilters import truncatechars

from agir.lib.form_fields import AdminRichEditorWidget
from agir.notifications.models import Announcement, Notification


class AnnouncementForm(forms.ModelForm):
    class Meta:
        fields = ("content", "icon", "link", "start_date", "end_date", "segment")
        widgets = {"content": AdminRichEditorWidget()}


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    form = AnnouncementForm
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
        return Announcement.objects.annotate(
            seen=Count(
                "notification",
                filter=Q(
                    notification__status__in=[
                        Notification.STATUS_SEEN,
                        Notification.STATUS_CLICKED,
                    ]
                ),
            ),
            clicked=Count(
                "notification",
                filter=Q(notification__status=Notification.STATUS_CLICKED),
            ),
        )

    def seen(self, announcement):
        return announcement.seen

    seen.short_description = "Vues"

    def clicked(self, announcement):
        return announcement.clicked

    clicked.short_description = "Clics"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("created", "person", "icon", "content_truncated", "status")
    fields = ("person", "content", "icon", "link", "status")
    autocomplete_fields = ("person",)

    def content_truncated(self, obj):
        return truncatechars(obj.content, 60)
