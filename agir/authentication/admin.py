from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import reverse
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters

from agir.lib.search import PrefixSearchQuery
from . import models

sensitive_post_parameters_m = method_decorator(sensitive_post_parameters())


@admin.register(models.Role)
class RoleAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("password", "last_login", "link")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )
    readonly_fields = ("last_login", "link")

    list_display = ("id", "type", "link", "is_staff", "is_superuser")
    list_filter = ("type", "is_staff", "is_superuser", "groups")
    filter_horizontal = ("groups", "user_permissions")

    # non utilisé, mais le champ de recherche n'apparaît pas s'il n'est pas assigné
    search_fields = ("person__search",)
    ordering = ("id",)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                person__search=PrefixSearchQuery(
                    search_term, config="simple_unaccented"
                )
            )

        use_distinct = False

        return queryset, use_distinct

    def link(self, obj):
        link_schema = '<a href="{}">{}</a>'

        if obj.type == obj.CLIENT_ROLE:
            return format_html(
                link_schema,
                reverse("admin:clients_client_change", args=(obj.client.pk,)),
                obj.client.name,
            )
        elif obj.type == obj.PERSON_ROLE:
            return format_html(
                link_schema,
                reverse("admin:people_person_change", args=(obj.person.pk,)),
                str(obj.person),
            )

    link.short_description = _("Lien vers la personne ou le client")

    def get_urls(self):
        urls = super(RoleAdmin, self).get_urls()

        # remove 'add' view: roles should only be created when adding persons or clients
        return urls[:2] + urls[3:]
