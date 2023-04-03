from django.contrib import admin
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe

from .. import models


class MembershipInline(admin.TabularInline):
    model = models.Membership
    fields = (
        "person_link",
        "membership_type",
        "gender",
        "description",
        "group_name",
    )
    readonly_fields = ("person_link", "gender", "description", "group_name")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("person")

    @admin.display(description="Personne")
    def person_link(self, obj):
        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse("admin:people_person_change", args=(obj.person.id,)),
                escape(obj.person),
            )
        )

    @admin.display(description="Genre", empty_value="-")
    def gender(self, obj):
        return obj.person.get_gender_display()

    @admin.display(description="Groupe d'origine", empty_value="-")
    def group_name(self, obj):
        if not obj or not obj.meta or not obj.meta.get("group_id"):
            return

        group_id = obj.meta.get("group_id")
        group_name = obj.meta.get("group_name", group_id)

        return mark_safe(
            '<a href="%s">%s</a>'
            % (
                reverse(
                    "admin:groups_supportgroup_change",
                    args=(group_id,),
                ),
                escape(group_name),
            )
        )

    def has_add_permission(self, request, obj=None):
        return False


class ExternalLinkInline(admin.TabularInline):
    extra = 0
    model = models.SupportGroupExternalLink
    fields = ("url", "label")
