from django.contrib import admin

from agir.telegram.models import TelegramSession, TelegramGroup


@admin.register(TelegramSession)
class TelegramSessionAdmin(admin.ModelAdmin):
    readonly_fields = ("phone_number", "session_string")

    def has_add_permission(self, request):
        return False


@admin.register(TelegramGroup)
class TelegramGroupAdmin(admin.ModelAdmin):
    autocomplete_fields = ("segment",)
    readonly_fields = ("telegram_users", "telegram_ids")
