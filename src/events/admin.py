from django.contrib import admin

from . import models


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Calendar)
class CalendarAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EventTag)
class EventTagAdmin(admin.ModelAdmin):
    pass
