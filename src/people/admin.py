from django.shortcuts import reverse
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from api.admin import admin_site

from .models import Person, PersonTag


@admin.register(Person, site=admin_site)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed', 'role_link')
    search_fields = ('emails__address', 'first_name', 'last_name',)

    fieldsets = (
        (None, {
            'fields': ('email', 'first_name', 'last_name',)
        }),
        (_('Dates'), {
            'fields': ('created', 'modified')
        }),
        (_('Paramètres mails'), {
            'fields': ('subscribed', 'bounced', 'bounced_date',)
        }),
        (_('Role correspondant'), {
            'fields': ('role_link',)
        })
    )

    readonly_fields = ('created', 'modified', 'role_link')

    def role_link(self, obj):
        return '<a href="%s">%s</a>' % (
            reverse('admin:authentication_role_change', args=[obj.role_id]),
            _('Voir le rôle')
        )
    role_link.allow_tags = True
    role_link.short_description = _('Lien vers le rôle')


@admin.register(PersonTag, site=admin_site)
class PersonTagAdmin(admin.ModelAdmin):
    pass
