from django.db.models import Count
from django.shortcuts import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html
from django.utils.translation import ugettext_lazy as _
from api.admin import admin_site
from admin_steroids.filters import AjaxFieldFilter

from .models import Person, PersonTag, PersonEmail, PersonForm
from events.models import RSVP
from groups.models import Membership

from front.utils import front_url

class RSVPInline(admin.TabularInline):
    model = RSVP
    can_add = False
    fields = ('event_link',)
    readonly_fields = ('event_link',)

    def event_link(self, obj):
        return mark_safe('<a href="%s">%s</a>' % (
            reverse('admin:events_event_change', args=(obj.event.id,)),
            escape(obj.event.name)
        ))

    def has_add_permission(self, request):
        return False


class MembershipInline(admin.TabularInline):
    model = Membership
    can_add = False
    fields = ('supportgroup_link', 'is_referent', 'is_manager')
    readonly_fields = ('supportgroup_link',)

    def supportgroup_link(self, obj):
        return mark_safe('<a href="%s">%s</a>' % (
            reverse('admin:groups_supportgroup_change', args=(obj.supportgroup.id,)),
            escape(obj.supportgroup.name)
        ))

    def has_add_permission(self, request):
        return False


class EmailInline(admin.TabularInline):
    model = PersonEmail
    readonly_fields = ('address',)
    extra = 0
    fields = ('address', '_bounced', 'bounced_date')


@admin.register(Person, site=admin_site)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'subscribed', 'role_link', 'created')
    list_display_links = ('email',)

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name',)
        }),
        (_('Dates'), {
            'fields': ('created', 'modified')
        }),
        (_('Paramètres mails'), {
            'fields': ('subscribed', 'event_notifications', 'group_notifications')
        }),
        (_('Paramètres de participation'), {
            'fields': ('draw_participation', )
        }),
        (_('Profil'), {
            'fields': ('gender', 'date_of_birth', 'tags')
        }),
        (_('Contact'), {
            'fields': (
                'contact_phone',
                'location_name',
                'location_address',
                'location_address1',
                'location_address2',
                'location_city',
                'location_zip',
                'location_state',
                'location_country',
            )
        }),
        (_('Role correspondant'), {
            'fields': ('role_link',)
        }),
        (_('Meta'), {
            'fields': ('meta',)
        })
    )

    readonly_fields = ('created', 'modified', 'role_link', 'supportgroups', 'events')

    search_fields = ('emails__address', 'first_name', 'last_name', 'location_zip')

    list_filter = (
        ('location_city', AjaxFieldFilter),
        ('location_zip', AjaxFieldFilter),
        ('tags'),
        ('subscribed', admin.BooleanFieldListFilter),
        ('draw_participation', admin.BooleanFieldListFilter),
        ('gender'),
    )

    inlines = (RSVPInline, MembershipInline, EmailInline)

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


@admin.register(PersonForm, site=admin_site)
class PersonFormAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug_link', 'published',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'published', 'submissions_number')
        }),
        (_('Champs'), {
            'fields': ('main_question', 'tags', 'personal_information', 'additional_fields')
        }),
        (_('Textes'), {
            'fields': ('description', 'confirmation_note')
         }),
    )

    readonly_fields = ('submissions_number', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(submissions_number=Count('submissions'))

    def slug_link(self, object):
        if object.slug:
            return format_html('<a href="{}">{}</a>', front_url('view_person_form', args=(object.slug,)), object.slug)
        else:
            return '-'
    slug_link.short_description = 'Slug'

    def submissions_number(self, object):
        return object.submissions_number
    submissions_number.short_description = 'Nombre de soumissions'
