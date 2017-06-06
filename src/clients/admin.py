from django.contrib import admin
from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _
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

    list_display = ('label', 'name', 'role_link')

    def role_link(self, obj):
        return '<a href="%s">%s</a>' % (
            reverse('admin:authentication_role_change', args=[obj.role_id]),
            _('Voir le rôle')
        )
    role_link.allow_tags = True
    role_link.short_description = _('Lien vers le rôle')

@admin.register(models.Scope, site=admin_site)
class ScopeAdmin(admin.ModelAdmin):
    pass
