from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import reverse
from django.template.response import TemplateResponse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from .forms import AddMemberForm


def add_member(model_admin, request, pk):
    if not model_admin.has_change_permission(request) or not request.user.has_perm(
        "people.select_person"
    ):
        raise PermissionDenied

    group = model_admin.get_object(request, pk)

    if group is None:
        raise Http404(_("Pas de groupe avec cet identifiant."))

    if request.method == "POST":
        form = AddMemberForm(group, model_admin, request.POST)

        if form.is_valid():
            membership = form.save()
            messages.success(
                request,
                _("{email} a bien été ajouté au groupe").format(
                    email=membership.person.display_email
                ),
            )

            return HttpResponseRedirect(
                reverse(
                    "%s:%s_%s_change"
                    % (
                        model_admin.admin_site.name,
                        group._meta.app_label,
                        group._meta.model_name,
                    ),
                    args=(group.pk,),
                )
            )
    else:
        form = AddMemberForm(group, model_admin)

    fieldsets = [(None, {"fields": ["person", "membership_type"]})]
    admin_form = admin.helpers.AdminForm(form, fieldsets, {})

    context = {
        "title": _("Ajouter un membre au groupe: %s") % escape(group.name),
        "adminform": admin_form,
        "form": form,
        "is_popup": True,
        "opts": model_admin.model._meta,
        "original": group,
        "change": True,
        "add": False,
        "save_as": False,
        "show_save": True,
        "has_delete_permission": model_admin.has_delete_permission(request, group),
        "has_add_permission": model_admin.has_add_permission(request),
        "has_change_permission": model_admin.has_change_permission(request, group),
        "has_view_permission": model_admin.has_view_permission(request, group),
        "has_editable_inline_admin_formsets": False,
        "media": model_admin.media + admin_form.media,
    }
    context.update(model_admin.admin_site.each_context(request))

    request.current_app = model_admin.admin_site.name

    return TemplateResponse(request, "admin/supportgroups/add_member.html", context)
