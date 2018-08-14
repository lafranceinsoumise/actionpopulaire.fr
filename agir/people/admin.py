import csv
from urllib.parse import urlencode

import django_otp
from django import forms
from django.urls import path, reverse_lazy
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import reverse
from django.contrib import admin
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django.utils.html import escape, format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.utils import display_for_value, unquote
from django.contrib.gis.admin import OSMGeoAdmin
from django.views.generic import RedirectView

from agir.api.admin import admin_site

from .actions.person_forms import validate_custom_fields
from .models import Person, PersonTag, PersonEmail, PersonForm, PersonFormSubmission
from agir.authentication.models import Role
from agir.events.models import RSVP
from agir.groups.models import Membership

from agir.lib.utils import front_url, generate_token_params
from agir.lib.admin import CenterOnFranceMixin
from agir.lib.search import PrefixSearchQuery
from agir.lib.form_fields import AdminRichEditorWidget
from agir.lib.forms import CoordinatesFormMixin


class PersonAdminForm(CoordinatesFormMixin, forms.ModelForm):
    pass


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
class PersonAdmin(CenterOnFranceMixin, OSMGeoAdmin):
    list_display = ('first_name', 'last_name', 'email', 'contact_phone', 'subscribed', 'role_link', 'created')
    list_display_links = ('email',)
    form = PersonAdminForm

    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'connection_params', 'role_link', 'role_totp_link')
        }),
        (_('Dates'), {
            'fields': ('created', 'modified', 'last_login')
        }),
        (_('Paramètres mails'), {
            'fields': ('subscribed', 'event_notifications', 'group_notifications')
        }),
        (_('Paramètres de participation'), {
            'fields': ('draw_participation', )
        }),
        (_('Profil'), {
            'fields': ('gender', 'date_of_birth', 'tags', 'mandates')
        }),
        (_('Contact et adresse'), {
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
                'coordinates',
                'coordinates_type',
                'redo_geocoding',
            )
        }),
        (_('Meta'), {
            'fields': ('meta',)
        })
    )

    readonly_fields = (
        'connection_params', 'created', 'modified', 'last_login', 'role_link', 'role_totp_link', 'supportgroups', 'events',
        'coordinates_type'
    )

    search_fields = ('emails__address', 'first_name', 'last_name', 'location_zip')

    list_filter = (
        ('tags'),
        ('subscribed', admin.BooleanFieldListFilter),
        ('draw_participation', admin.BooleanFieldListFilter),
        ('gender'),
    )

    inlines = (RSVPInline, MembershipInline, EmailInline)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            filter = PrefixSearchQuery(search_term, config='simple_unaccented')
            queryset = queryset.filter(search=filter)

        use_distinct = False

        return queryset, use_distinct

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('emails')

    def role_link(self, obj):
        return format_html(
            '<a href="{link}">{text}</a>',
            link=reverse('admin:authentication_role_change', args=[obj.role_id]),
            text=_('Voir le rôle')
        )
    role_link.short_description = _('Lien vers le rôle')

    def role_totp_link(self, obj):
        return format_html_join(
            mark_safe('<br>'),
            '<a href="{}">{}</a>',
            ((reverse('admin:otp_totp_totpdevice_change', args=[device.id]), device.name)
             for device in django_otp.devices_for_user(obj.role, confirmed=False))
        )
    role_totp_link.short_description = _('Lien vers les téléphones Authenticator enregistrés')

    def connection_params(self, obj):
        if obj.pk:
            return urlencode(generate_token_params(obj))
        else:
            return '-'
    connection_params.short_description = _("Paramètres de connexion")
    connection_params.help_text = _("A copier/coller à la fin d'une url agir pour obtenir un lien qui connecte automatiquement.")

    def last_login(self, obj):

        if obj.role_id:
            return display_for_value(obj.role.last_login, '-')
        else:
            return '-'
    last_login.short_description = Role._meta.get_field('last_login').verbose_name


@admin.register(PersonTag, site=admin_site)
class PersonTagAdmin(admin.ModelAdmin):
    list_display = ('label', 'exported')

    actions = ('set_as_exported', 'set_as_not_exported')

    def set_as_exported(self, request, queryset):
        queryset.update(exported=True)
    set_as_exported.short_description = _('Exporter ces tags')

    def set_as_not_exported(self, request, queryset):
        queryset.update(exported=False)
    set_as_not_exported.short_description = _('Ne plus exporter')


class PersonFormForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        widgets = {'description': AdminRichEditorWidget(), 'confirmation_note': AdminRichEditorWidget()}

    def clean_custom_fields(self):
        value = self.cleaned_data['custom_fields']
        validate_custom_fields(value)

        return value


class PersonFormAdminMixin:
    def get_form_submission_qs(self, form):
        return form.submissions.all()

    def generate_result_table(self, form, only_text=False):
        submission_qs = self.get_form_submission_qs(form)
        fields = [field for fieldset in form.custom_fields for field in fieldset['fields']]
        submissions = []

        for submission in submission_qs:
            data = [submission.data.get(field['id'], 'NA') for field in fields]
            submissions.append([submission.pk] + [submission.modified]
                            + [submission.person if only_text is False else submission.person.email]
                            + data)

        headers = ['ID', 'Date', 'Personne'] + [(field.get('label') or Person._meta.get_field(field['id']).verbose_name) for field in fields]

        return {'form': form, 'headers': headers, 'submissions': submissions}

    def view_results(self, request, pk):
        if not self.has_change_permission(request) or not request.user.has_perm('people.change_personform'):
            raise PermissionDenied

        form = PersonForm.objects.get(id=pk)
        table = self.generate_result_table(form)

        context = {
            'has_change_permission': True,
            'title': _('Réponses du formulaire: %s') % escape(form.title),
            'opts': self.model._meta,
            'form': table['form'],
            'headers': table['headers'],
            'submissions': table['submissions']
        }

        return TemplateResponse(
            request,
            'admin/personforms/view_results.html',
            context,
        )

    def download_results(self, request, pk):
        if not self.has_change_permission(request) or not request.user.has_perm('people.change_personform'):
            raise PermissionDenied

        form = PersonForm.objects.get(id=pk)
        table = self.generate_result_table(form, only_text=True)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(form.slug)

        writer = csv.writer(response)
        writer.writerow(table['headers'])
        for submission in table['submissions']:
            writer.writerow(submission)

        return response


@admin.register(PersonForm, site=admin_site)
class PersonFormAdmin(PersonFormAdminMixin, admin.ModelAdmin):
    form = PersonFormForm
    list_display = ('title', 'slug_link', 'published',)

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'published', 'start_time', 'end_time', 'send_answers_to')
        }),
        (_('Soumissions'), {
            'fields': ('submissions_number', 'simple_link', 'action_buttons')
        }),
        (_('Champs'), {
            'fields': ('main_question', 'tags', 'custom_fields')
        }),
        (_('Textes'), {
            'fields': ('description', 'confirmation_note', 'send_confirmation', 'before_message', 'after_message')
         }),
    )

    readonly_fields = ('submissions_number', 'simple_link', 'action_buttons')

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.annotate(submissions_number=Count('submissions'))

    def get_urls(self):
        return [
            path('<int:pk>/view_results/', self.admin_site.admin_view(self.view_results), name="people_personform_view_results"),
            path('<int:pk>/download_results/', self.admin_site.admin_view(self.download_results), name="people_personform_download_results"),
        ] + super().get_urls()

    def slug_link(self, object):
        if object.slug:
            return format_html('<a href="{}">{}</a>', front_url('view_person_form', args=(object.slug,)), object.slug)
        else:
            return '-'
    slug_link.short_description = 'Slug'

    def action_buttons(self, object):
        if object._state.adding:
            return mark_safe('-')
        else:
            return format_html(
                '<a href="{view_results_link}" class="button">Voir les résultats</a><br>'
                '<a href="{download_results_link}" class="button">Télécharger les résultats</a><br>',
                view_results_link=reverse('admin:people_personform_view_results', args=(object.pk,)),
                download_results_link=reverse('admin:people_personform_download_results', args=(object.pk,)),
            )
    action_buttons.short_description = _("Actions")

    def simple_link(self, object):
        if object.slug:
            return format_html('<a href="{0}">{0}</a>', front_url('view_person_form', args=(object.slug,)))
        else:
            return '-'
    simple_link.short_description = 'Lien vers le formulaire'

    def submissions_number(self, object):
        return object.submissions_number
    submissions_number.short_description = 'Nombre de soumissions'

@admin.register(PersonFormSubmission, site=admin_site)
class PersonFormSubmissionAdmin(admin.ModelAdmin):
    def delete_view(self, request, object_id, extra_context=None):
        self.personform = self.get_object(request, unquote(object_id)).form
        return super().delete_view(request, object_id, extra_context)

    def response_delete(self, request, obj_display, obj_id):
        return HttpResponseRedirect(reverse('admin:people_personform_change', args=[self.personform.pk]))

    def get_urls(self):
        return [
            path('<object_id>/delete/', self.admin_site.admin_view(self.delete_view), name='people_personformsubmission_delete')
        ]
