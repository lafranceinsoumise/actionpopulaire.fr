import re
from io import BytesIO

import pandas as pd
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import reverse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.html import escape
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from glom import glom, T

from .forms import AddMemberForm
from ..models import SupportGroup
from ..tasks import maj_boucles
from ...lib.utils import front_url


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


def maj_membres_boucles_departementales(model_admin, request, pk):
    if not model_admin.has_change_permission(request):
        raise PermissionDenied

    group = model_admin.get_object(request, pk)

    if group is None:
        raise Http404("Pas de groupe avec cet identifiant")

    response = HttpResponseRedirect(
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

    if group.type != SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE:
        messages.warning(
            request,
            "La mise à jour automatique des membres est disponible uniquement pour les boucles départementales",
        )
        return response

    if group.location_departement_id:
        code = group.location_departement_id
    else:
        code = re.search("^\d\d?|$", group.name).group()
        code = f"99-{int(code):02d}" if code else None

    if not code:
        messages.warning(
            request,
            "Le département ou la circonscription FE n'ont pas pu être retrouvés pour cette boucle",
        )
        return response

    result = maj_boucles([code])
    result = list(result.items())

    if not result:
        messages.warning(
            request,
            "Le département ou la circonscription FE n'ont pas pu être retrouvés pour cette boucle",
        )
        return response

    lieu, count = result[0]

    if not count:
        messages.warning(
            request,
            "Le département ou la circonscription FE n'ont pas pu être retrouvés pour cette boucle",
        )
        return response

    existing, created, deleted = count
    message = (
        f"La boucle {lieu} a été mise à jour · Membres existants : {existing} "
        f"· Membres supprimés : {deleted} · Membres ajoutés : {created}"
    )
    messages.success(request, message)
    return response


def format_memberships_for_export(group):
    memberships = group.memberships.select_related("person", "supportgroup")
    groups = {
        str(g.id): g.name
        for g in SupportGroup.objects.filter(
            id__in=list(
                memberships.filter(meta__group_id__isnull=False).values_list(
                    "meta__group_id", flat=True
                )
            )
        ).only("id", "name")
    }

    spec = {
        "nom": ("person.last_name", lambda name: name.upper()),
        "prénom": ("person.first_name", lambda name: name.title()),
        "pseudo": "person.display_name",
        "statut": T.get_membership_type_display(),
        "description": "description",
        "nom du groupe d'origine": (
            "meta",
            lambda meta: groups.get(meta["group_id"], "") if "group_id" in meta else "",
        ),
        "page du groupe d'origine": (
            "meta",
            lambda meta: front_url(
                "view_group", kwargs={"pk": meta["group_id"]}, absolute=True
            )
            if "group_id" in meta
            else "",
        ),
        "email": "person.email",
        "téléphone": "person.contact_phone",
        "code postal": "person.location_zip",
        "ville": "person.location_city",
        "pays": "person.location_country",
        "inscription action populaire": T.person.created.astimezone(
            timezone.get_current_timezone()
        )
        .replace(microsecond=0)
        .isoformat(),
        "inscription dans le groupe": T.created.astimezone(
            timezone.get_current_timezone()
        )
        .replace(microsecond=0)
        .isoformat(),
    }

    if group.type != SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE:
        del spec["description"]
        del spec["nom du groupe d'origine"]
        del spec["page du groupe d'origine"]

    return glom(memberships, [spec])


def export_memberships_to_xlsx(group):
    memberships = format_memberships_for_export(group)
    res = pd.DataFrame(memberships)

    with BytesIO() as excel_file:
        res.to_excel(
            excel_file,
            engine="xlsxwriter",
            sheet_name=slugify(group.name)[:31],
            index=False,
        )
        filename = f"membres_{slugify(group.name)}_{timezone.now().date()}.xlsx"
        response = HttpResponse(
            excel_file.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


def export_memberships_to_csv(group):
    memberships = format_memberships_for_export(group)
    res = pd.DataFrame(memberships)
    filename = f"membres_{slugify(group.name)}_{timezone.now().date()}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={filename}"
    res.to_csv(response, index=False)

    return response


def export_memberships(modeladmin, request, pk, as_format):
    if not modeladmin.has_change_permission(request) or not request.user.has_perm(
        "people.export_people"
    ):
        raise PermissionDenied

    group = modeladmin.get_object(request, pk)

    if group is None:
        raise Http404("Pas de groupe avec cet identifiant")

    if as_format == "csv":
        return export_memberships_to_csv(group)
    if as_format == "xlsx":
        return export_memberships_to_xlsx(group)

    return Http404(f"Le format {as_format} n'est pas supporté pour l'export")
