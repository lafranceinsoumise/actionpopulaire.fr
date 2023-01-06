from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from agir.lib.admin.form_fields import AutocompleteSelectModel
from agir.people.actions.export import liaisons_to_csv_response, people_to_csv_response
from agir.people.models import PersonTag

ADMIN_PERSON_EXPORT_LIMIT = 500


def export_people_to_csv(modeladmin, request, queryset):
    return people_to_csv_response(queryset[:ADMIN_PERSON_EXPORT_LIMIT])


export_people_to_csv.short_description = f"Exporter les personnes en CSV (max. {ADMIN_PERSON_EXPORT_LIMIT} personnnes par export)"
export_people_to_csv.allowed_permissions = ["export"]
export_people_to_csv.select_across = True
export_people_to_csv.max_items = ADMIN_PERSON_EXPORT_LIMIT


def export_liaisons_to_csv(modeladmin, request, queryset):
    return liaisons_to_csv_response(queryset.liaisons())


export_liaisons_to_csv.short_description = f"Exporter les correspondant·es en CSV"
export_liaisons_to_csv.allowed_permissions = ["export"]
export_liaisons_to_csv.select_across = True


def unsubscribe_from_all_newsletters(person):
    with transaction.atomic():
        person.notification_subscriptions.all().delete()
        person.newsletters = list()
        person.save()


class AddPersonTagForm(forms.Form):
    tag = forms.ModelChoiceField(
        PersonTag.objects.all(), required=True, label="Tag à ajouter"
    )

    def __init__(self, model_admin, request, people, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.people = people
        self.fields["tag"].widget = RelatedFieldWidgetWrapper(
            AutocompleteSelectModel(
                PersonTag,
                admin_site=model_admin.admin_site,
                choices=self.fields["tag"].choices,
            ),
            people.first()._meta.get_field("tags").remote_field,
            admin_site=model_admin.admin_site,
            can_add_related=request.user.has_perm("people.add_persontag"),
            can_change_related=request.user.has_perm("people.change_persontag"),
        )

    def save(self):
        tag = self.cleaned_data["tag"]
        tag.people.add(*self.people)
        return tag


def bulk_add_tag(modeladmin, request, queryset):
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied

    if "_apply_action" in request.POST:
        form = AddPersonTagForm(modeladmin, request, queryset, data=request.POST)

        if form.is_valid():
            tag = form.save()
            modeladmin.message_user(
                request,
                f"Le tag '{tag.label}' a bien été ajouté à {queryset.count()} personne(s)",
            )
            return HttpResponseRedirect(request.get_full_path())
    else:
        form = AddPersonTagForm(modeladmin, request, queryset)

    fieldsets = [(None, {"fields": ["tag"]})]
    admin_form = admin.helpers.AdminForm(form, fieldsets, {})

    person_count = queryset.count()

    if person_count > 1:
        title = f"Ajouter un tag à {person_count} personne(s)"
    else:
        title = "Ajouter un tag à une personne"

    context = {
        "action_name": "bulk_add_tag",
        "title": title,
        "adminform": admin_form,
        "form": form,
        "is_popup": False,
        "opts": modeladmin.model._meta,
        "original": queryset,
        "change": False,
        "add": False,
        "save_as": False,
        "show_save": True,
        "show_save_and_continue": False,
        "has_delete_permission": False,
        "has_add_permission": False,
        "has_change_permission": modeladmin.has_change_permission(request),
        "has_view_permission": modeladmin.has_view_permission(request),
        "media": modeladmin.media + admin_form.media,
    }
    context.update(modeladmin.admin_site.each_context(request))

    return TemplateResponse(request, "admin/people/person/bulk_add_tag.html", context)


bulk_add_tag.short_description = "Ajouter un tag aux personnes sélectionnées"
bulk_add_tag.allowed_permissions = ["bulk_add_tag"]
bulk_add_tag.select_across = True
