from django.contrib import admin
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.forms import OSMWidget
from api.admin import admin_site

from . import models


class EventForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = (
            'name', 'description', 'start_time', 'end_time', 'calendar', 'tags', 'location_name', 'location_address1',
            'location_address2', 'location_city', 'location_zip', 'location_state', 'location_country', 'coordinates',
            'contact_name', 'contact_email', 'contact_phone', 'nb_id', 'nb_path',
        )
        widgets = {
            'coordinates': OSMWidget
        }


@admin.register(models.Event, site=admin_site)
class EventAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('id', 'name',)
        }),
        (_('Informations'), {
            'fields': ('description', 'start_time', 'end_time', 'calendar', 'tags',)
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

    form = EventForm


@admin.register(models.Calendar, site=admin_site)
class CalendarAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EventTag, site=admin_site)
class EventTagAdmin(admin.ModelAdmin):
    pass
