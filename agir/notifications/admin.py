from django import forms
from django.contrib import admin
from django.db.models import Count, Q
from django.template.defaultfilters import truncatechars

from agir.lib.form_fields import AdminRichEditorWidget
from agir.notifications.models import Announcement


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
    )

    list_display = ("__str__", "start_date", "end_date")

    def get_queryset(self, request):
        return Announcement.objects.all()
