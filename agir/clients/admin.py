from django.contrib import admin
from django import forms
from django.forms import CheckboxSelectMultiple
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from ..api.admin import admin_site

from . import models
from .scopes import scopes


class ClientForm(forms.ModelForm):
    scopes = forms.MultipleChoiceField(
        choices=[(scope.name, scope.description) for scope in scopes],
        widget=CheckboxSelectMultiple
    )


@admin.register(models.Client, site=admin_site)
class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    fieldsets = (
        (None, {
            'fields': ('label', 'name', 'description')
        }),
        ('OAuth', {
            'fields': ('oauth_enabled', 'trusted', 'uris', 'scopes')
        }),
        (_('Role correspondant'), {
            'fields': ('role_link',)
        })
    )

    list_display = ('label', 'name', 'role_link')
    readonly_fields = ('created', 'modified', 'role_link')

    def role_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_role_change', args=[obj.role_id]),
            _('Voir le rôle')
        )
    role_link.short_description = _('Lien vers le rôle')
