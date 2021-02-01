from django.contrib import admin
from reversion.admin import VersionAdmin

from agir.msgs.models import SupportGroupMessage


@admin.register(SupportGroupMessage)
class SupportGroupMessageAdmin(VersionAdmin):
    readonly_fields = ("author", "supportgroup", "linked_event", "text", "image")

    def has_add_permission(self, request, obj=None):
        return False
