from django.conf import settings
from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.gis.admin import OSMGeoAdmin
from django.utils.translation import ugettext_lazy as _
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.shortcuts import reverse
from django.db.models import Count
from django.contrib.admin.utils import unquote
from api.admin import admin_site
from admin_steroids.filters import AjaxFieldFilter
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404, StreamingHttpResponse
from django.contrib.admin.options import IS_POPUP_VAR
from django.template.response import TemplateResponse

from groups.actions import groups_to_csv_lines
from lib.admin import CenterOnFranceMixin
from front.utils import front_url

from .. import models
from ..actions.promo_codes import get_next_promo_code
from .forms import AddMemberForm, SupportGroupAdminForm


class MembershipInline(admin.TabularInline):
    model = models.Membership
    fields = ('person_link', 'is_referent', 'is_manager')
    readonly_fields = ('person_link', )

    def person_link(self, obj):
        return mark_safe('<a href="%s">%s</a>' % (
            reverse('admin:people_person_change', args=(obj.person.id,)),
            escape(obj.person.email)
        ))
    person_link.short_description = _("Personne")

    def has_add_permission(self, request):
        return False


@admin.register(models.SupportGroup, site=admin_site)
class SupportGroupAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    form = SupportGroupAdminForm
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'link', 'created', 'modified', 'action_buttons', 'promo_code')
        }),
        (_('Informations'), {
            'fields': ('type', 'subtypes', 'description', 'allow_html', 'image', 'tags', 'published')
        }),
        (_('Lieu'), {
            'fields': ('location_name', 'location_address1', 'location_address2', 'location_city', 'location_zip',
                       'location_state', 'location_country', 'coordinates', 'coordinates_type', 'redo_geocoding')
        }),
        (_('Contact'), {
            'fields': ('contact_name', 'contact_email', 'contact_phone')
        }),
        (_('NationBuilder'), {
            'fields': ('nb_id', 'nb_path', 'location_address', )
        }),
    )
    inlines = (MembershipInline,)
    readonly_fields = ('id', 'link', 'action_buttons', 'created', 'modified', 'coordinates_type', 'promo_code')
    date_hierarchy = 'created'

    list_display = ('name', 'type', 'published', 'location_short', 'membership_count', 'created', 'referent')
    list_filter = (
        'type',
        ('location_city', AjaxFieldFilter),
        ('location_zip', AjaxFieldFilter),
        'published',
        'tags',
        'subtypes',
    )

    search_fields = ('name', 'description', 'location_city', 'location_country')
    actions = ('export_groups',)

    def promo_code(self, object):
        if object.pk and object.tags.filter(label=settings.PROMO_CODE_TAG).exists():
            return get_next_promo_code(object)
        else:
            return '-'
    promo_code.short_description = _("Code promo du mois")

    def referent(self, object):
        referent = object.memberships.filter(is_referent=True).first()
        if (referent):
            return referent.person.email

        return ''
    referent.short_description = _('Animateurice')

    def location_short(self, object):
        return _('{zip} {city}, {country}').format(
            zip=object.location_zip,
            city=object.location_city,
            country=object.location_country.name
        )
    location_short.short_description = _("Lieu")
    location_short.admin_order_field = 'location_zip'

    def membership_count(self, object):
        return format_html(
            _('{nb} (<a href="{link}">Ajouter un membre</a>)'),
            nb=object.membership_count,
            link=reverse('admin:groups_supportgroup_add_member', args=(object.pk,))
        )
    membership_count.short_description = _("Nombre de membres")
    membership_count.admin_order_field = 'membership_count'

    def link(self, object):
        if object.pk:
            return format_html('<a href="{0}">{0}</a>', front_url('view_group', kwargs={'pk': object.pk}))
        else:
            return mark_safe('-')
    link.short_description = _("Page sur le site")

    def action_buttons(self, object):
        if object._state.adding:
            return mark_safe('-')
        else:
            return format_html(
                '<a href="{add_member_link}" class="button">Ajouter un membre</a> <small>Attention : cliquer'
                ' sur ces boutons quitte la page et perd vos modifications courantes.</small>',
                add_member_link=reverse('admin:groups_supportgroup_add_member', args=(object.pk,))
            )
    action_buttons.short_description = _("Actions")

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(membership_count=Count('memberships'))

    def export_groups(self, request, queryset):
        response =  StreamingHttpResponse(
            groups_to_csv_lines(queryset),
            content_type='text/csv',
        )
        response['Content-Disposition'] = 'inline; filename=export_groups_{}.csv'.format(
            timezone.now().astimezone(timezone.get_default_timezone()).strftime('%Y%m%d_%H%M')
        )

        return response
    export_groups.short_description = _("Exporter les groupes en CSV")

    def get_urls(self):
        return [
            url(r'^(.+)/add_member/', self.admin_site.admin_view(self.add_member), name="groups_supportgroup_add_member")
        ] + super().get_urls()

    def add_member(self, request, id):
        if not self.has_change_permission(request) or not request.user.has_perm('people.view_person'):
            raise PermissionDenied

        group = self.get_object(request, unquote(id))

        if group is None:
            raise Http404(_("Pas de groupe avec cet identifiant."))

        if request.method == "POST":
            form = AddMemberForm(group, request.POST)

            if form.is_valid():
                membership = form.save()
                messages.success(request, _("{email} a bien été ajouté au groupe").format(email=membership.person.email))

                return HttpResponseRedirect(
                    reverse(
                        '%s:%s_%s_change' % (
                            self.admin_site.name,
                            group._meta.app_label,
                            group._meta.model_name,
                        ),
                        args=(group.pk,),
                    )
                )
        else:
            form = AddMemberForm(group)

        fieldsets = [(None, {'fields': ['person']})]
        admin_form = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': _('Ajouter un membre au groupe: %s') % escape(group.name),
            'adminform': admin_form,
            'form': form,
            'is_popup': (IS_POPUP_VAR in request.POST or
                         IS_POPUP_VAR in request.GET),
            'opts': self.model._meta,
            'original': group,
            'change': False,
            'add': False,
            'save_as': True,
            'show_save': False,
            'has_delete_permission': False,
            'has_add_permission': False,
            'has_change_permission': True,
            'media': self.media + admin_form.media
        }
        context.update(self.admin_site.each_context(request))

        request.current_app = self.admin_site.name

        return TemplateResponse(
            request,
            'admin/supportgroups/add_member.html',
            context,
        )


@admin.register(models.SupportGroupTag, site=admin_site)
class SupportGroupTagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SupportGroupSubtype, site=admin_site)
class SupportGroupSubtypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'description', 'type')
    list_filter = ('type',)
