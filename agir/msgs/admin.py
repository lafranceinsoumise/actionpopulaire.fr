from django.contrib import admin
from django.contrib.admin.options import TabularInline
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment, UserReport
from agir.groups.models import Membership


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


@admin.register(SupportGroupMessageComment)
class SupportGroupMessageCommentAdmin(VersionAdmin):
    fields = ("created", "modified", "author", "text", "image", "msg", "deleted")
    readonly_fields = ("created", "modified", "author", "text", "image", "msg")
    list_display = (
        "text_excerpt",
        "author",
        "msg",
        "report_count",
        "created",
        "deleted",
    )
    list_filter = ("deleted", ReportListFilter)
    search_fields = ("=id", "=message__id", "message__subject", "author__search")
    model = SupportGroupMessageComment

    def text_excerpt(self, object):
        return truncatechars(object.text, 20)

    text_excerpt.short_description = "Texte"

    def msg(self, object):
        href = reverse(
            "admin:msgs_supportgroupmessage_change",
            args=[object.message.pk],
        )
        return format_html(
            f'<a href="{href}"><strong>{truncatechars(object.message.subject, 40)}</strong><br />({object.message.pk})</a>'
        )

    msg.short_description = "Message initial"

    def report_count(self, object):
        return object.reports.count()

    report_count.short_description = "Signalements"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class InlineSupportGroupMessageCommentAdmin(TabularInline):
    fields = (
        "created",
        "modified",
        "author",
        "text",
        "history",
        "report_count",
        "deleted",
    )
    readonly_fields = (
        "created",
        "modified",
        "author",
        "text",
        "history",
        "report_count",
    )
    model = SupportGroupMessageComment

    def history(self, object):
        return format_html(
            '<a href="{}">Historique</a>',
            reverse("admin:msgs_supportgroupmessagecomment_history", args=[object.pk]),
        )

    def report_count(self, object):
        return object.reports.count()

    report_count.short_description = "Signalements"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SupportGroupMessage)
class SupportGroupMessageAdmin(VersionAdmin):
    fields = (
        "supportgroup",
        "created",
        "modified",
        "author",
        "subject",
        "text",
        "image",
        "linked_event",
        "deleted",
        "required_membership_type",
        "is_locked",
        "readonly",
    )
    readonly_fields = (
        "created",
        "modified",
        "author",
        "supportgroup",
        "linked_event",
        "subject",
        "text",
        "image",
    )
    list_display = (
        "subject",
        "text_excerpt",
        "author",
        "group",
        "event",
        "created",
        "comment_count",
        "report_count",
        "deleted",
        "required_membership_type",
    )
    search_fields = ("=id", "subject", "supportgroup__name", "author__search")
    list_filter = ("deleted", ReportListFilter, RequiredMembershipListFilter)

    inlines = [
        InlineSupportGroupMessageCommentAdmin,
    ]

    def text_excerpt(self, object):
        return truncatechars(object.text, 20)

    text_excerpt.short_description = "Texte"

    def comment_count(self, object):
        return SupportGroupMessageComment.objects.filter(message=object.pk).count()

    comment_count.short_description = "Nombre de commentaires"

    def report_count(self, object):
        return object.reports.count()

    report_count.short_description = "Signalements"

    def event(self, object):
        if object.linked_event_id is None:
            return "-"
        href = reverse(
            "admin:events_event_change",
            args=[object.linked_event.pk],
        )
        return format_html(
            f'<a href="{href}"><strong>{truncatechars(object.linked_event.name, 40)}</strong><br />({object.linked_event.pk})</a>'
        )

    event.short_description = "Événement"

    def group(self, object):
        if object.supportgroup is None:
            return "-"
        href = reverse(
            "admin:groups_supportgroup_change",
            args=[object.supportgroup.pk],
        )
        return format_html(
            f'<a href="{href}"><strong>{truncatechars(object.supportgroup.name, 40)}</strong><br />({object.supportgroup.pk})</a>'
        )

    group.short_description = "Groupe"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    fields = ("reporter", "reported_object_link", "reported_object_author", "created")
    list_fields = (
        "reporter",
        "reported_object_link",
        "reported_object_author",
        "created",
    )
    search_fields = ("reporter__search", "=object_id")
    readonly_fields = fields
    list_display = fields

    def reported_object_link(self, obj):
        return format_html(
            '<a href="{}">{}</a>',
            reverse(
                f"admin:{obj.content_type.app_label}_{obj.content_type.model}_change",
                args=[obj.object_id],
            ),
            str(obj.reported_object),
        )

    reported_object_link.short_description = "Message signalé"

    def reported_object_author(self, obj):
        if obj.reported_object and obj.reported_object.author:
            return format_html(
                '<a href="{}">{}</a>',
                reverse(
                    f"admin:people_person_change",
                    args=[obj.reported_object.author.id],
                ),
                str(obj.reported_object.author),
            )

    reported_object_author.short_description = "Auteur du message signalé"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
