from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.html import format_html, escape
from django import forms
from api.admin import admin_site
from admin_steroids.filters import AjaxFieldFilter

from groups.models import SupportGroup
from lib.admin import CenterOnFranceMixin
from lib.forms import CoordinatesFormMixin
from lib.form_fields import AdminRichEditorWidget
from front.utils import front_url

from . import models


class EventAdminForm(CoordinatesFormMixin, forms.ModelForm):
    class Meta:
        exclude = (
            'id', 'organizers', 'attendees'
        )
        widgets = {
            'description': AdminRichEditorWidget()
        }


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


class OrganizerConfigForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.fields['as_group'].queryset = SupportGroup.objects.filter(memberships__person=self.instance.person, memberships__is_manager=True)
        except (AttributeError, ObjectDoesNotExist):
            pass


class OrganizerConfigInline(admin.TabularInline):
    model = models.OrganizerConfig
    form = OrganizerConfigForm
    fields = ('person_link', 'as_group')
    readonly_fields = ('person_link', )

    def get_form(self, obj):
        print('lol')
        form = super().get_form()
        form.fields['as_group'].queryset = SupportGroup.objects.filter(memberships__person=obj.person, memberships__is_manager=True)

    def person_link(self, obj):
        return mark_safe('<a href="%s">%s</a>' % (
            reverse('admin:people_person_change', args=(obj.person.id,)),
            escape(obj.person.email)
        ))
    person_link.short_description = _("Personne")

    def has_add_permission(self, request):
        return False


@admin.register(models.Event, site=admin_site)
class EventAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    form = EventAdminForm

    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'link', 'created', 'modified')
        }),
        (_('Informations'), {
            'fields': ('description', 'allow_html', 'image', 'start_time', 'end_time', 'calendar', 'tags', 'published'),
        }),
        (_('Lieu'), {
            'fields': ('location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
                       'location_state', 'location_country', 'coordinates', 'coordinates_type', 'redo_geocoding')
        }),
        (_('Contact'), {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        (_('NationBuilder'), {
            'fields': ('nb_id', 'nb_path', 'location_address')
        })
    )

    inlines = (OrganizerConfigInline,)

    readonly_fields = ('id', 'link', 'organizers', 'created', 'modified', 'coordinates_type')
    date_hierarchy = 'start_time'

    list_display = ('name', 'published', 'calendar_title', 'location_short', 'attendee_count', 'start_time', 'created')
    list_filter = (
        ('location_city', AjaxFieldFilter),
        ('location_zip', AjaxFieldFilter),
        EventStatusFilter,
        'calendar',
        'published',
        'tags',
    )

    search_fields = ('name', 'description', 'location_city', 'location_country')

    def location_short(self, object):
        return _('{zip} {city}, {country}').format(
            zip=object.location_zip,
            city=object.location_city,
            country=object.location_country.name
        )
    location_short.short_description = _("Lieu")
    location_short.admin_order_field = 'location_city'

    def calendar_title(self, object):
        return object.calendar.name
    calendar_title.short_description = _('Agenda')
    calendar_title.admin_order_field = 'calendar__name'

    def attendee_count(self, object):
        return object.attendee_count
    attendee_count.short_description = _("Nombre de personnes inscrites")
    attendee_count.admin_order_field = 'attendee_count'

    def link(self, object):
        if object.pk:
            return format_html('<a href="{0}">{0}</a>', front_url('view_event', kwargs={'pk': object.pk}))
        else:
            return '-'
    link.short_description = _("Page sur le site")

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(attendee_count=Sum(1 + F('rsvps__guests')))


@admin.register(models.Calendar, site=admin_site)
class CalendarAdmin(admin.ModelAdmin):
    fields = ('name', 'slug', 'link', 'user_contributed', 'description', 'image')
    list_display = ('name', 'slug', 'user_contributed')
    readonly_fields = ('link',)

    def link(self, object):
        if object.slug:
            return format_html('<a href="{0}">{0}</a>', front_url('view_calendar', kwargs={'slug': object.slug}))
        else:
            return '-'
    link.short_description = _("Lien vers l'agenda")


@admin.register(models.EventTag, site=admin_site)
class EventTagAdmin(admin.ModelAdmin):
    pass
