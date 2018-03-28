from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.admin import OSMGeoAdmin
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.html import format_html, escape
from django.http import StreamingHttpResponse
from django import forms
from api.admin import admin_site
from admin_steroids.filters import AjaxFieldFilter

from groups.models import SupportGroup
from lib.admin import CenterOnFranceMixin
from lib.forms import CoordinatesFormMixin
from lib.form_fields import AdminRichEditorWidget
from front.utils import front_url

from . import models
from .actions import events_to_csv_lines


class EventAdminForm(CoordinatesFormMixin, forms.ModelForm):
    calendars = forms.ModelMultipleChoiceField(
        queryset=models.Calendar.objects.all(),
        required=False,
        label='Agendas',
        help_text=_('Maintenez appuyé « Ctrl », ou « Commande (touche pomme) » sur un Mac, pour en sélectionner plusieurs.')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['calendars'].initial = self.instance.calendars.all()

    def _save_m2m(self):
        super()._save_m2m()

        current_calendars = set(c.pk for c in self.instance.calendars.all())
        new_calendars = set(c.pk for c in self.cleaned_data['calendars'])

        # delete items for removed calendars
        models.CalendarItem.objects.filter(
            event=self.instance, calendar_id__in=current_calendars - new_calendars
        ).delete()

        # add items for added calendars
        models.CalendarItem.objects.bulk_create(
            models.CalendarItem(event=self.instance, calendar_id=c) for c in new_calendars - current_calendars
        )

    class Meta:
        exclude = (
            'id', 'organizers', 'attendees'
        )
        widgets = {
            'description': AdminRichEditorWidget(),
            'report_content': AdminRichEditorWidget(),
        }


class EventStatusFilter(admin.SimpleListFilter):
    title = _('Statut')

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


class EventHasReportFilter(admin.SimpleListFilter):
    title = _('Compte-rendu présent')

    parameter_name = 'has_report'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Présent')),
            ('no', _('Absent')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(report_content='')
        if self.value() == 'no':
            return queryset.filter(report_content='')


class OrganizerConfigInline(admin.TabularInline):
    model = models.OrganizerConfig
    fields = ('person_link', 'as_group')
    readonly_fields = ('person_link', )

    def get_form(self, obj):
        form = super().get_form()
        form.fields['as_group'].queryset = SupportGroup.objects.filter(memberships__person=obj.person, memberships__is_manager=True)

    def person_link(self, obj):
        return mark_safe(format_html(
            '<a href="{}">{}</a>',
            reverse('admin:people_person_change', args=(obj.person.id,)),
            escape(obj.person.email)
        ))
    person_link.short_description = _("Personne")

    def has_add_permission(self, request):
        return False


class EventImageInline(admin.TabularInline):
    model = models.EventImage
    fields = ('image_link', 'author_link', 'legend')
    readonly_fields = ('image_link', 'author_link',)
    extra = 0

    def has_add_permission(self, request):
        return False

    def image_link(self, obj):
        return mark_safe(format_html(
            '<a href="{}"><img src="{}"></a>',
            obj.image.url,
            obj.image.admin_thumbnail.url
        ))
    image_link.short_description = _('Image')

    def author_link(self, obj):
        return mark_safe(format_html(
            '<a href="{}">{}</a>',
            reverse('admin:people_person_change', args=(obj.author.id,)),
            escape(obj.author.email)
        ))
    author_link.short_description = _("Auteur")


@admin.register(models.Event, site=admin_site)
class EventAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    form = EventAdminForm

    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'link', 'created', 'modified')
        }),
        (_('Informations'), {
            'fields': ('subtype', 'description', 'allow_html', 'image', 'start_time', 'end_time', 'calendars', 'tags', 'published'),
        }),
        (_('Lieu'), {
            'fields': ('location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
                       'location_state', 'location_country', 'coordinates', 'coordinates_type', 'redo_geocoding')
        }),
        (_('Contact'), {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        (_('Compte-rendu'), {
            'fields': ('report_content', 'report_image')
        }),
        (_('NationBuilder'), {
            'fields': ('nb_id', 'nb_path', 'location_address')
        })
    )

    inlines = (OrganizerConfigInline, EventImageInline)

    readonly_fields = ('id', 'link', 'organizers', 'created', 'modified', 'coordinates_type')
    date_hierarchy = 'start_time'

    list_display = ('name', 'published', 'calendar_names', 'location_short', 'attendee_count', 'start_time', 'created')
    list_filter = (
        'published',
        'subtype__type',
        'subtype',
        'calendars',
        EventHasReportFilter,
        EventStatusFilter,
        ('location_city', AjaxFieldFilter),
        ('location_zip', AjaxFieldFilter),
        'tags',
    )

    search_fields = ('name', 'description', 'location_city', 'location_country')

    actions = ('export_events',)

    def location_short(self, object):
        return _('{zip} {city}, {country}').format(
            zip=object.location_zip,
            city=object.location_city,
            country=object.location_country.name
        )
    location_short.short_description = _("Lieu")
    location_short.admin_order_field = 'location_city'

    def calendar_names(self, object):
        return ', '.join(c.name for c in object.calendars.all())
    calendar_names.short_description = _('Agendas')

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

    def export_events(self, request, queryset):
        response =  StreamingHttpResponse(
            events_to_csv_lines(queryset),
            content_type='text/csv',
        )
        response['Content-Disposition'] = 'inline; filename=export_events_{}.csv'.format(
            timezone.now().astimezone(timezone.get_default_timezone()).strftime('%Y%m%d_%H%M')
        )

        return response
    export_events.short_description = _("Exporter les événements en CSV")


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


@admin.register(models.EventSubtype, site=admin_site)
class EventSubtypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'description', 'type')
    list_filter = ('type',)
