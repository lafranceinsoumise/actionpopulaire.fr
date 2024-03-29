from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from .. import models
from ...lib.admin.utils import display_link, admin_url


class MembershipInlineForm(forms.ModelForm):
    description = forms.CharField(required=False, label=_("Description"))

    def has_instance(self):
        return (
            self.instance is not None
            and hasattr(self.instance, "supportgroup")
            and self.instance.supportgroup is not None
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.has_instance():
            return

        self.fields["description"].initial = self.instance.description

    def full_clean(self):
        super().full_clean()

        if not self.has_instance() or not hasattr(self, "cleaned_data"):
            return

        if self.cleaned_data.get("description", None):
            self.instance.description = self.cleaned_data["description"]

    class Meta:
        model = models.Membership
        fields = ()


class MembershipInline(admin.TabularInline):
    model = models.Membership
    form = MembershipInlineForm
    extra = 0
    fields = (
        "person_link",
        "gender",
        "membership_type",
        "description",
        "is_finance_manager_value",
    )
    boucle_departementale_fields = (
        "person_link",
        "gender",
        "membership_type",
        "description_value",
        "group_name",
        "is_finance_manager_value",
    )
    readonly_fields = (
        "person_link",
        "gender",
        "group_name",
        "description_value",
        "is_finance_manager_value",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("supportgroup", "person")

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
            return "-"

        group_id = obj.meta.get("group_id")
        group_name = obj.meta.get("group_name", group_id)

        return display_link(
            admin_url(
                "admin:groups_supportgroup_change",
                args=(group_id,),
            ),
            group_name,
        )

    @admin.display(description="Description")
    def description_value(self, obj):
        return obj and obj.description

    @admin.display(description="Gestionnaire financier", boolean=True)
    def is_finance_manager_value(self, obj):
        return obj and obj.is_finance_manager

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and obj.type == obj.TYPE_BOUCLE_DEPARTEMENTALE:
            return False

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.has_automatic_memberships:
            return False

        return super().has_change_permission(request, obj)

    def get_fields(self, request, obj=None):
        if obj and obj.type == obj.TYPE_BOUCLE_DEPARTEMENTALE:
            return self.boucle_departementale_fields

        return super().get_fields(request, obj)


class ExternalLinkInline(admin.TabularInline):
    extra = 0
    model = models.SupportGroupExternalLink
    fields = ("url", "label")
