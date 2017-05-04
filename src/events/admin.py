from django.contrib import admin
from api.admin import admin_site

from . import models


@admin.register(models.Event, site=admin_site)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Calendar, site=admin_site)
class CalendarAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EventTag, site=admin_site)
class EventTagAdmin(admin.ModelAdmin):
    pass
