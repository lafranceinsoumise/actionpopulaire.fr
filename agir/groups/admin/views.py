from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.shortcuts import reverse
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.contrib.admin.options import IS_POPUP_VAR
from django.template.response import TemplateResponse

from .forms import AddMemberForm


def add_member(model_admin, request, pk):
    if not model_admin.has_change_permission(request) or not request.user.has_perm('people.view_person'):
        raise PermissionDenied

    group = model_admin.get_object(request, pk)

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
                        model_admin.admin_site.name,
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
        'opts': model_admin.model._meta,
        'original': group,
        'change': False,
        'add': False,
        'save_as': True,
        'show_save': False,
        'has_delete_permission': False,
        'has_add_permission': False,
        'has_change_permission': True,
        'media': model_admin.media + admin_form.media
    }
    context.update(model_admin.admin_site.each_context(request))

    request.current_app = model_admin.admin_site.name

    return TemplateResponse(
        request,
        'admin/supportgroups/add_member.html',
        context,
    )
