from django.contrib import admin
from api.admin import admin_site

from . import models

@admin.register(models.Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('label', 'name', 'description')
        }),
        ('OAuth', {
            'fields': ('oauth_enabled', 'trusted', 'uris', 'scopes')
        }),
    )


@admin.register(models.Scope, site=admin_site)
class ScopeAdmin(admin.ModelAdmin):
    pass
