from django import forms
from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from django.shortcuts import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from . import models
from .scopes import scopes


class ClientForm(forms.ModelForm):
    scopes = forms.MultipleChoiceField(
        choices=[(scope.name, scope.description) for scope in scopes],
        widget=CheckboxSelectMultiple,
    )


admin.site.unregister(models.Client)


@admin.register(models.Client)
class ClientAdmin(admin.ModelAdmin):
    form = ClientForm
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "description",
                    "created",
                    "modified",
                    "client_id",
                    "client_secret",
                )
            },
        ),
        (
            "OAuth",
            {
                "fields": (
                    "authorization_grant_type",
                    "client_type",
                    "skip_authorization",
                    "redirect_uris",
                    "scopes",
                )
            },
        ),
        (_("Role correspondant"), {"fields": ("role_link",)}),
    )

    list_display = (
        "name",
        "authorization_grant_type",
        "client_type",
        "skip_authorization",
        "role_link",
    )
    readonly_fields = ("created", "modified", "role_link")
    list_filter = ("client_type", "authorization_grant_type", "skip_authorization")
    radio_fields = {
        "client_type": admin.HORIZONTAL,
        "authorization_grant_type": admin.VERTICAL,
    }

    def role_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:authentication_role_change", args=[obj.role_id]),
            _("Voir le rôle"),
        )

    role_link.short_description = _("Lien vers le rôle")
