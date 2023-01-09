from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from agir.events.models import RSVP
from agir.groups.models import Membership
from agir.people.models import PersonEmail, PersonQualification


class RSVPInline(admin.TabularInline):
    model = RSVP
    can_add = False
    fields = ("event_link",)
    readonly_fields = ("event_link",)

    def event_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:events_event_change", args=(obj.event.id,)),
            obj.event.name,
        )

    def has_add_permission(self, request, obj=None):
        return False


class MembershipInline(admin.TabularInline):
    model = Membership
    can_add = False
    fields = ("supportgroup_link", "membership_type")
    readonly_fields = ("supportgroup_link",)

    def supportgroup_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:groups_supportgroup_change", args=(obj.supportgroup.id,)),
            obj.supportgroup.name,
        )

    def has_add_permission(self, request, obj=None):
        return False


class EmailInline(admin.TabularInline):
    model = PersonEmail
    readonly_fields = ("address",)
    extra = 0
    fields = ("address", "_bounced", "bounced_date")

    def has_add_permission(self, request, obj=None):
        return False


class PersonQualificationInline(admin.TabularInline):
    template = "admin/people/includes/person_qualification_tabular.html"
    model = PersonQualification
    extra = 0
    fields = ("qualification", "start_time", "end_time", "is_effective")
    readonly_fields = ("qualification", "start_time", "end_time", "is_effective")
    show_change_link = True

    def is_effective(self, obj):
        return obj.is_effective

    is_effective.short_description = "En cours"
    is_effective.boolean = True
