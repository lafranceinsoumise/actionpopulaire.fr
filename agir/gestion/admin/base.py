from functools import partial

from django.contrib.admin.options import BaseModelAdmin
from django.utils.html import format_html

from agir.gestion.actions import afficher_commentaires
from agir.gestion.admin.forms import CommentairesForm
from agir.lib.admin import get_admin_link


class BaseMixin(BaseModelAdmin):
    search_fields = ("numero",)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            return queryset.search(search_term)
        return queryset, False

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        return partial(form, user=request.user)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + (
            "bloc_commentaires",
            "numero_",
        )

    def numero_(self, obj):
        if obj.id:
            return format_html('<a href="{}">{}</a>', get_admin_link(obj), obj.numero)
        else:
            return "Attribué à la création"

    numero_.short_description = "Numéro automatique"

    def bloc_commentaires(self, obj):
        if obj and obj.commentaires:
            return afficher_commentaires(obj)
        return "Aucun commentaire."

    bloc_commentaires.short_description = "Commentaires"


class BaseAdminMixin(BaseMixin):
    form = CommentairesForm
