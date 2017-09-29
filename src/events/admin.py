from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.encoding import force_text
from api.admin import admin_site
from ajax_select import make_ajax_form

from lib.admin import CenterOnFranceMixin

from . import models


class EventStatusFilter(admin.SimpleListFilter):
    title = _('Status')

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('all', _('All')),
            ('finished', _('Terminé')),
            ('current', _('En cours')),
            ('upcoming', _('À venir')),
        )

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': (lookup == 'upcoming' and self.value() is None) or self.value() == force_text(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }


    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == 'finished':
            return queryset.filter(end_time__lt=now)
        elif self.value() == 'current':
            return queryset.filter(start_time__lte=now, end_time__gte=now)
        elif self.value() == 'all':
            return queryset
        else:
            return queryset.filter(start_time__gt=now)


@admin.register(models.Event, site=admin_site)
class EventAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'created', 'modified')
        }),
        (_('Informations'), {
            'fields': ('description', 'start_time', 'end_time', 'calendar', 'tags', 'published'),
        }),
        (_('Organisation'), {
            'fields': ('organizers',)
        }),
        (_('Lieu'), {
            'fields': ('location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
                       'location_state', 'location_country', 'coordinates', 'coordinates_type')
        }),
        (_('Contact'), {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        (_('NationBuilder'), {
            'fields': ('nb_id', 'nb_path',)
        })
    )

    form = make_ajax_form(models.Event, {'organizers': 'people'})

    filter_horizontal = ('organizers',)

    readonly_fields = ('id', 'organizers', 'created', 'modified', 'coordinates_type')
    date_hierarchy = 'start_time'

    list_display = ('name', 'published', '_calendar', 'location_short', 'attendee_count', 'start_time', 'created')
    list_filter = (EventStatusFilter, 'calendar', 'published')

    search_fields = ('name', 'description', 'location_city', 'location_country')

    def location_short(self, object):
        return _('{zip} {city}, {country}').format(
            zip=object.location_zip,
            city=object.location_city,
            country=object.location_country.name
        )
    location_short.short_description = _("Lieu")
    location_short.admin_order_field = 'location_city'

    def _calendar(self, object):
        return object.calendar.description

    _calendar.short_description = _('Agenda')
    _calendar.admin_order_field = 'calendar__description'

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
