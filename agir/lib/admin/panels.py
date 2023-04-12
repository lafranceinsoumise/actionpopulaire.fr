from functools import partial
from typing import Iterable

from django.contrib.admin import helpers
from django.contrib.admin.options import IS_POPUP_VAR, BaseModelAdmin
from django.db.models import (
    ForeignObjectRel,
    ForeignObject,
    OneToOneRel,
    ManyToOneRel,
    ManyToManyRel,
    ManyToManyField,
)
from django.db.models.fields.related import RelatedField
from django.urls import reverse
from django.utils.html import escape, format_html, format_html_join
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic.base import ContextMixin


class CenterOnFranceMixin:
    # for some reason it has to be in projected coordinates
    default_lon = 364043
    default_lat = 5850840
    default_zoom = 5


class DisplayContactPhoneMixin:
    def display_contact_phone(self, object):
        if object.contact_phone:
            return object.contact_phone.as_international
        return "-"

    display_contact_phone.short_description = _("Numéro de contact")
    display_contact_phone.admin_order_field = "contact_phone"


class AdminViewMixin(ContextMixin, View):
    model_admin = None

    def get_admin_helpers(
        self, form, fields: Iterable[str] = None, fieldsets=None, readonly_fields=None
    ):
        if fieldsets is None:
            fieldsets = [(None, {"fields": list(fields)})]
        if readonly_fields is None:
            readonly_fields = []

        model_admin = self.kwargs.get("model_admin") or self.model_admin

        admin_form = helpers.AdminForm(
            form=form,
            fieldsets=fieldsets,
            model_admin=model_admin,
            prepopulated_fields={},
            readonly_fields=readonly_fields,
        )

        return {
            "adminform": admin_form,
            "errors": helpers.AdminErrorList(form, []),
            "media": model_admin.media + admin_form.media,
        }

    def get_context_data(self, **kwargs):
        model_admin = self.kwargs.get("model_admin") or self.model_admin

        # noinspection PyProtectedMember
        kwargs.setdefault("opts", model_admin.model._meta)
        kwargs.setdefault("add", False)
        kwargs.setdefault("change", False)
        kwargs.setdefault(
            "is_popup",
            IS_POPUP_VAR in self.request.POST or IS_POPUP_VAR in self.request.GET,
        )
        kwargs.setdefault("save_as", False)
        kwargs.setdefault(
            "has_add_permission", model_admin.has_add_permission(self.request)
        )
        kwargs.setdefault(
            "has_change_permission", model_admin.has_change_permission(self.request)
        )
        kwargs.setdefault(
            "has_view_permission", model_admin.has_view_permission(self.request)
        )
        kwargs.setdefault("has_editable_inline_admin_formsets", False)
        kwargs.setdefault("has_delete_permission", False)
        kwargs.setdefault("show_close", False)

        kwargs.update(model_admin.admin_site.each_context(request=self.request))

        return super().get_context_data(**kwargs)


class PersonLinkMixin:
    def person_link(self, obj):
        if obj.person is not None:
            return mark_safe(
                '<a href="%s">%s</a>'
                % (
                    reverse("admin:people_person_change", args=(obj.person.id,)),
                    escape(obj.person),
                )
            )

        return "Aucune"

    person_link.short_description = "Personne"


class AddRelatedLinkMixin(BaseModelAdmin):
    """Mixin pour les interfaces d'administration qui ajoute automatiquement des champs de liens et de liste vers les
    objets liés

    Les champs de modèles de type
    """

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)

        self._additional_related_fields = []

        for f in model._meta.get_fields():
            # RelatedField est l'ancêtre de tous les champs liés direct
            # ForeignObjectRel est l'ancêtre de tous les champs liés inverses
            if (
                isinstance(f, (RelatedField, ForeignObjectRel))
                and f.related_model is not None
            ):
                if isinstance(f, ForeignObjectRel):
                    attr_name = f.get_accessor_name()
                    verbose_name = f.related_model._meta.verbose_name_plural
                else:
                    attr_name = f.name
                    verbose_name = f.verbose_name

                view_name = "admin:%s_%s_change" % (
                    f.related_model._meta.app_label,
                    f.related_model._meta.model_name,
                )

                # ForeignObject est l'ancêtre de tous les champs liés directs à destination unique
                # OneToOneRel est l'unique champ lié inverse à destination unique
                if isinstance(f, (ForeignObject, OneToOneRel)):
                    get_link = partial(
                        self._get_link, attr_name=attr_name, view_name=view_name
                    )
                    get_link.short_description = verbose_name
                    get_link.admin_order_field = f.name

                    link_attr_name = f"{attr_name}_link"
                    if not hasattr(self, link_attr_name):
                        setattr(self, link_attr_name, get_link)
                        self._additional_related_fields.append(link_attr_name)

                # ManyToManyField est le seul champ lié direct à destination multiple
                # ManyToOneRel et ManyToManyRel sont les deux champs inverses à destination multiple
                elif isinstance(f, (ManyToOneRel, ManyToManyRel, ManyToManyField)):
                    get_list = partial(
                        self._get_list, attr_name=attr_name, view_name=view_name
                    )

                    get_list.short_description = verbose_name

                    link_attr_name = f"{attr_name}_list"
                    if not hasattr(self, link_attr_name):
                        setattr(self, link_attr_name, get_list)
                        self._additional_related_fields.append(link_attr_name)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not obj or not obj.id:
            return readonly_fields
        return readonly_fields + tuple(self._additional_related_fields)

    def _get_link(self, obj, *, attr_name, view_name):
        if hasattr(obj, attr_name) and getattr(obj, attr_name, None) is not None:
            value = getattr(obj, attr_name)
            return format_html(
                '<a href="{link}">{text}</a>',
                link=reverse(view_name, args=(value.pk,)),
                text=str(value),
            )
        return "-"

    def _get_list(self, obj, *, attr_name, view_name):
        qs = getattr(obj, attr_name).all()
        if not qs.exists():
            return "-"
        return format_html_join(
            mark_safe("<br>"),
            '<a href="{}">{}</a>',
            ((reverse(view_name, args=(obj.pk,)), str(obj)) for obj in qs),
        )
