from django.contrib import admin
from api.admin import admin_site

from . import models


@admin.register(models.SupportGroup, site=admin_site)
class SupportGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SupportGroupTag, site=admin_site)
class SupportGroupTagAdmin(admin.ModelAdmin):
    pass
