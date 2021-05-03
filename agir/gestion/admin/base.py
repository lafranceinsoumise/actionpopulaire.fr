from functools import partial

from django.contrib.admin.options import BaseModelAdmin, ModelAdmin
from django.utils.html import format_html

from agir.gestion.admin.forms import CommentairesForm
from agir.lib.admin import get_admin_link


class BaseMixin(BaseModelAdmin):
    search_fields = ("numero",)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            return queryset.search(search_term)
        return queryset, False

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + ("numero_",)

    def numero_(self, obj):
        if obj.id:
            return format_html('<a href="{}">{}</a>', get_admin_link(obj), obj.numero)
        else:
            return "Attribué à la création"

    numero_.short_description = "Numéro automatique"


class BaseAdminMixin(BaseMixin, ModelAdmin):
    form = CommentairesForm

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        return partial(form, user=request.user)

    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        if obj and hasattr(obj, "commentaires"):
            context.setdefault("montrer_commentaires", True)
            context.setdefault("commentaires", obj.commentaires.filter(cache=False))
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj
        )
