from django.contrib import admin
from api.admin import admin_site

from . import models

@admin.register(models.Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Scope, site=admin_site)
class ScopeAdmin(admin.ModelAdmin):
    pass
