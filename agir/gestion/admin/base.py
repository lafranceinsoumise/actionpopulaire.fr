from django.contrib.admin.options import BaseModelAdmin, ModelAdmin
from django.urls import path
from django.utils.html import format_html

from agir.gestion.admin.forms import CommentaireForm
from agir.gestion.admin.views import (
    CacherCommentaireView,
    AjouterCommentaireView,
    TransitionView,
)
from agir.gestion.models import Commentaire
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
    def render_change_form(
        self, request, context, add=False, change=False, form_url="", obj=None
    ):
        if obj and hasattr(obj, "commentaires"):
            context.setdefault(
                "commentaires_todo",
                obj.commentaires.filter(type=Commentaire.Type.TODO, cache=False),
            )
            context.setdefault(
                "commentaires_rem",
                obj.commentaires.filter(type=Commentaire.Type.REM, cache=False),
            )
            context.setdefault("commentaire_form", CommentaireForm())

        if obj and hasattr(obj, "todos"):
            context.setdefault("todos", obj.todos())

        if obj and hasattr(obj, "transitions"):
            transitions = obj.transitions
            for t in transitions:
                t.disabled = t.refus(obj, request.user)
            context.setdefault("transitions", transitions)

        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url, obj=obj
        )

    def get_urls(self):
        urls = super().get_urls()
        opts = self.model._meta

        if hasattr(self.model, "commentaires"):
            urls = [
                path(
                    "commenter/<int:object_id>",
                    self.admin_site.admin_view(
                        AjouterCommentaireView.as_view(model=self.model)
                    ),
                    name=f"{opts.app_label}_{opts.model_name}_commenter",
                ),
                path(
                    "cacher_commentaire/<int:pk>/",
                    self.admin_site.admin_view(
                        CacherCommentaireView.as_view(model_admin=self)
                    ),
                    name=f"{opts.app_label}_{opts.model_name}_cacher_commentaire",
                ),
                *urls,
            ]

        if hasattr(self.model, "transitions"):
            urls = [
                path(
                    "<int:object_id>/transition/",
                    self.admin_site.admin_view(
                        TransitionView.as_view(model=self.model)
                    ),
                    name=f"{opts.app_label}_{opts.model_name}_transition",
                ),
                *urls,
            ]

        return urls
