from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import F, Sum
from django.utils import timezone
from api.admin import admin_site

from lib.admin import CenterOnFranceMixin

from . import models


class EventStatusFilter(admin.SimpleListFilter):
    title = _('Status')

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('finished', _('Terminé')),
            ('current', _('En cours')),
            ('upcoming', _('Prévu')),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'finished':
            return queryset.filter(end_time__lt=now)
        elif self.value() == 'current':
            return queryset.filter(start_time__lte=now, end_time__gte=now)
        elif self.value() == 'upcoming':
            return queryset.filter(start_time__gt=now)
        else:
            return queryset


@admin.register(models.Event, site=admin_site)
class EventAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    fieldsets = (
        (None, {
            'fields': ('id', 'name',)
        }),
        (_('Informations'), {
            'fields': ('description', 'start_time', 'end_time', 'calendar', 'tags', 'published')
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
    date_hierarchy = 'created'

    list_display = ('name', 'location_short', 'attendee_count', 'start_time')
    list_filter = (EventStatusFilter, 'calendar')

    search_fields = ('name', 'description', 'location_city', 'location_country')

    def location_short(self, object):
        return _('{zip} {city}, {country}').format(
            zip=object.location_zip,
            city=object.location_city,
            country=object.location_country.name
        )
    location_short.short_description = _("Lieu")
    location_short.admin_order_field = 'location_city'

    def attendee_count(self, object):
        return object.attendee_count
    attendee_count.short_description = _("Nombre de personnes inscrites")
    attendee_count.admin_order_field = 'attendee_count'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(attendee_count=Sum(1 + F('rsvps__guests')))


@admin.register(models.Calendar, site=admin_site)
class CalendarAdmin(admin.ModelAdmin):
    pass


@admin.register(models.EventTag, site=admin_site)
class EventTagAdmin(admin.ModelAdmin):
    pass
