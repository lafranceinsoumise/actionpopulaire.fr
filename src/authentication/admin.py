from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters

from api.admin import admin_site

from . import models

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


@admin.register(models.Role, site=admin_site)
class RoleAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('password', 'last_login')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    readonly_fields = ('last_login',)


    list_display = ('id', 'type', 'link', 'is_staff', 'is_superuser')
    list_filter = ('type', 'is_staff', 'is_superuser', 'groups')
    filter_horizontal = ('groups', 'user_permissions',)

    search_fields = ('id', )
    ordering = ('id',)

    def link(self, obj):
        link_schema = '<a href="%s">%s</a>'

        if obj.type == obj.CLIENT_ROLE:
            return link_schema % (
                reverse('admin:clients_client_change', args=(obj.client.pk,)),
                _('Voir le client')
            )
        elif obj.type == obj.PERSON_ROLE:
            return link_schema % (
                reverse('admin:people_person_change', args=(obj.person.pk,)),
                _('Voir la personne')
            )
    link.allow_tags = True
    link.short_description = _('Lien vers la personne ou le client')

    def get_urls(self):
        urls = super(RoleAdmin, self).get_urls()

        # remove 'add' view: roles should only be created when adding persons or clients
        return urls[:2] + urls[3:]
