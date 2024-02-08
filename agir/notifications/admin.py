from django.contrib import admin

from agir.lib.admin.autocomplete_filter import AutocompleteRelatedModelFilter
from agir.lib.admin.utils import display_link
from agir.notifications.models import Subscription


class SubscriberAutocompleteFilter(AutocompleteRelatedModelFilter):
    title = "Personne"
    parameter_name = "person_id"
    field_name = "person"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "created",
        "person_link",
        "display_type",
        "activity_type",
        "membership_group",
    )
    list_filter = (SubscriberAutocompleteFilter, "type", "activity_type")

    @admin.display(description="Personne", ordering="person")
    def person_link(self, obj):
        return display_link(obj.person)

    @admin.display(description="Type", ordering="person")
    def display_type(self, obj):
        obj_type = obj.get_type_display()

        if obj.type == obj.SUBSCRIPTION_EMAIL:
            return f"✉️ {obj_type}"

        if obj.type == obj.SUBSCRIPTION_PUSH:
            return f"📱 {obj_type}"

        return obj_type

    @admin.display(description="Groupe d'action")
    def membership_group(self, obj):
        if not obj or not obj.membership:
            return "-"

        return display_link(obj.membership.supportgroup)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        if (
            f"{self.model._meta.app_label}/{self.model._meta.model_name}"
            in request.path
        ):
            return False
        return True

    class Media:
        pass
