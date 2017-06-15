from django.contrib import admin
from django import forms
from django.contrib.gis.forms import OSMWidget
from django.utils.translation import ugettext_lazy as _
from api.admin import admin_site

from . import models


class SupportGroupForm(forms.ModelForm):
    class Meta:
        model = models.SupportGroup
        fields = (
            'name', 'description', 'tags', 'location_name', 'location_address1',
            'location_address2', 'location_city', 'location_zip', 'location_state', 'location_country', 'coordinates',
            'contact_name', 'contact_email', 'contact_phone', 'nb_id', 'nb_path',
        )
        widgets = {
            'coordinates': OSMWidget
        }


@admin.register(models.SupportGroup, site=admin_site)
class SupportGroupAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('id', 'name',)
        }),
        (_('Informations'), {
            'fields': ('description', 'tags',)
        }),
        (_('Lieu'), {
            'fields': ('location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
                       'location_state', 'location_country', 'coordinates')
        }),
        (_('Contact'), {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        (_('NationBuilder'), {
            'fields': ('nb_id', 'nb_path',)
        })
    )

    readonly_fields = ('id',)

    form = SupportGroupForm


@admin.register(models.SupportGroupTag, site=admin_site)
class SupportGroupTagAdmin(admin.ModelAdmin):
    pass
