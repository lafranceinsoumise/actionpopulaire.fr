from django.contrib import admin

from . import models


@admin.register(models.SupportGroup)
class SupportGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SupportGroupTag)
class SupportGroupTagAdmin(admin.ModelAdmin):
    pass
