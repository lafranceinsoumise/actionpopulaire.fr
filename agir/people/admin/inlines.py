from django.contrib import admin
from django.db.models import Exists, OuterRef
from django.urls import reverse
from django.utils.html import format_html

from agir.events.models import Event
from agir.groups.models import Membership, SupportGroupSubtype
from agir.lib.admin.inlines import NonrelatedTabularInline
from agir.lib.admin.utils import display_link
from agir.people.models import PersonEmail, PersonQualification


class RSVPInline(NonrelatedTabularInline):
    model = Event
    can_add = False
    can_delete = False
    fields = readonly_fields = ("event_link", "event_date", "location_city")

    def get_form_queryset(self, obj):
        return obj.events.all()

    def save_new_instance(self, parent, instance):
        instance.save()
        parent.events.add(instance)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("event")

    @admin.display(description="Événement")
    def event_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:events_event_change", args=(obj.id,)),
            obj.name,
        )

    @admin.display(description="Date")
    def event_date(self, obj):
        return obj.get_simple_display_date()

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class MembershipInline(admin.TabularInline):
    model = Membership
    can_add = False
    fields = ("supportgroup_link", "published", "certified", "membership_type")
    readonly_fields = ("supportgroup_link", "published", "certified")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("supportgroup", "person", "person__public_email")
        )

    @admin.display(
        description="Groupe",
    )
    def supportgroup_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse("admin:groups_supportgroup_change", args=(obj.supportgroup.id,)),
            obj.supportgroup.name,
        )

    @admin.display(description="Publié", boolean=True)
    def published(self, obj):
        return obj.supportgroup.published

    @admin.display(description="Certifié", boolean=True)
    def certified(self, obj):
        return obj.supportgroup.is_certified

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
    fields = readonly_fields = (
        "person_link",
        "supportgroup_link",
        "qualification_link",
        "interval",
        "is_effective",
    )
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Type de statut", ordering="qualification")
    def qualification_link(self, obj):
        return display_link(obj.qualification)

    @admin.display(description="Personne", ordering="person")
    def person_link(self, obj):
        return display_link(obj.person)

    @admin.display(description="Groupe", ordering="supportgroup")
    def supportgroup_link(self, obj):
        return display_link(obj.supportgroup)

    @admin.display(description="Durée", ordering="start_time")
    def interval(self, obj):
        return obj.get_range_display()

    @admin.display(description="En cours", boolean=True)
    def is_effective(self, obj):
        return obj.is_effective
