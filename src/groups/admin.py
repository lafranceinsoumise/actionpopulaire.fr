from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils.translation import ugettext_lazy as _
from django.db.models import Count
from api.admin import admin_site

from lib.admin import CenterOnFranceMixin
from . import models


class MembershipInline(admin.TabularInline):
    model = models.Membership
    can_add = False
    fields = ('person', 'is_referent', 'is_manager')
    readonly_fields = ('person',)

    def has_add_permission(self, request):
        return False


@admin.register(models.SupportGroup, site=admin_site)
class SupportGroupAdmin(CenterOnFranceMixin, OSMGeoAdmin):
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
        }),
    )
    inlines = (MembershipInline,)
    readonly_fields = ('id',)
    date_hierarchy = 'created'

    list_display = ('name', 'location_short', 'membership_count')

    search_fields = ('name', 'description', 'location_city', 'location_country')

    def location_short(self, object):
        return _('{zip} {city}, {country}').format(
            zip=object.location_zip,
            city=object.location_city,
            country=object.location_country.name
        )
    location_short.short_description = _("Lieu")
    location_short.admin_order_field = 'location_zip'

    def membership_count(self, object):
        return object.membership_count
    membership_count.short_description = _("Nombre de membres")
    membership_count.admin_order_field = 'membership_count'

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(membership_count=Count('memberships'))


@admin.register(models.SupportGroupTag, site=admin_site)
class SupportGroupTagAdmin(admin.ModelAdmin):
    pass
