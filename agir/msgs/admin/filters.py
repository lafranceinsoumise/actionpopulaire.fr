from django.contrib import admin

from agir.groups.models import Membership, SupportGroup
from agir.lib.admin.autocomplete_filter import AutocompleteSelectModelBaseFilter
from agir.people.models import Person


class MessageSupportGroupFilter(AutocompleteSelectModelBaseFilter):
    title = "groupe"
    filter_model = SupportGroup
    parameter_name = "supportgroup"

    def get_queryset_for_field(self):
        return SupportGroup.objects.all()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supportgroup_id=self.value())
        else:
            return queryset


class CommentSupportGroupFilter(MessageSupportGroupFilter):
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(message__supportgroup_id=self.value())
        else:
            return queryset


class AuthorFilter(AutocompleteSelectModelBaseFilter):
    title = "auteur·ice"
    filter_model = Person
    parameter_name = "author"

    def get_queryset_for_field(self):
        return Person.objects.all()

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(author_id=self.value())
        else:
            return queryset


class ReportListFilter(admin.SimpleListFilter):
    title = "signalements reçus"
    parameter_name = "reports"

    def lookups(self, request, model_admin):
        return ("1", "Au moins un signalement"), ("0", "Aucun signalement")

    def queryset(self, request, queryset):
        if self.value():
            value = self.value() == "0"
            return queryset.filter(reports__isnull=value)
        return queryset


class RequiredMembershipListFilter(admin.SimpleListFilter):
    title = "visibilité de groupe"
    parameter_name = "required_membership_type"

    def lookups(self, request, model_admin):
        return (
            (Membership.MEMBERSHIP_TYPE_FOLLOWER, "Abonné·e"),
            (Membership.MEMBERSHIP_TYPE_MEMBER, "Membre actif·ve"),
            (Membership.MEMBERSHIP_TYPE_MANAGER, "Gestionnaire"),
            (Membership.MEMBERSHIP_TYPE_REFERENT, "Animateur·ice"),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(required_membership_type=self.value())
        return queryset
