from django.contrib import admin
from django.contrib.admin.options import TabularInline
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from reversion.admin import VersionAdmin

from agir.groups.models import Membership, SupportGroup
from agir.lib.admin.autocomplete_filter import AutocompleteSelectModelBaseFilter
from agir.lib.admin.utils import display_link, admin_url
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment, UserReport
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


class MessageAdminMixin:
    fields = (
        "id",
        "created",
        "modified",
        "author_link",
        "text",
        "image",
        "deleted",
    )
    readonly_fields = (
        "id",
        "author_link",
        "text",
        "image",
        "created",
        "modified",
    )
    list_display = (
        "id",
        "deleted",
        "author_link",
        "text_preview",
        "created",
        "report_count",
    )

    @admin.display(description="Auteur·ice")
    def author_link(self, obj):
        return display_link(obj.author)

    @admin.display(description="Texte")
    def text_preview(self, obj):
        return format_html(
            "<details style='width:200px;' open>"
            "<summary style='cursor:pointer;'><strong>{}</strong></summary>"
            "<blockquote>{}</blockquote>"
            "</details>",
            obj.message.subject if hasattr(obj, "message") else obj.subject,
            mark_safe(obj.text),
        )

    @admin.display(description="Nombre de signalements")
    def report_count(self, obj):
        count = obj.reports.count()

        if count == 0:
            return "-"

        return format_html(
            "<strong>{}</strong> " "<a href={}>(voir les signalements)</a>",
            count,
            admin_url(
                "admin:msgs_userreport_changelist",
                query={
                    "content_type": ContentType.objects.get(
                        app_label=self.model._meta.app_label,
                        model=self.model._meta.model_name,
                    ).id,
                    "object_id": str(obj.id),
                },
            ),
        )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    class Media:
        pass


@admin.register(SupportGroupMessageComment)
class SupportGroupMessageCommentAdmin(MessageAdminMixin, VersionAdmin):
    fields = (
        "id",
        "created",
        "modified",
        "author_link",
        "message_link",
        "text",
        "image",
        "deleted",
    )
    readonly_fields = (
        "id",
        "author_link",
        "message_link",
        "text",
        "image",
        "created",
        "modified",
    )
    list_display = (
        "id",
        "deleted",
        "message_link",
        "author_link",
        "text_preview",
        "created",
        "modified",
        "report_count",
    )
    list_filter = (AuthorFilter, CommentSupportGroupFilter, ReportListFilter, "deleted")
    search_fields = ("=id", "=message__id", "message__subject", "author__search")
    model = SupportGroupMessageComment

    @admin.display(description="Message")
    def message_link(self, obj):
        return display_link(obj.message, obj.message.pk)


class InlineSupportGroupMessageCommentAdmin(TabularInline, MessageAdminMixin):
    fields = (
        "created",
        "modified",
        "author_link",
        "text_excerpt",
        "history",
        "report_count",
        "deleted",
    )
    readonly_fields = (
        "created",
        "modified",
        "author_link",
        "text_excerpt",
        "history",
        "report_count",
    )
    model = SupportGroupMessageComment
    show_change_link = True
    can_delete = False
    extra = 0

    def history(self, obj):
        return format_html(
            '<a href="{}">Historique</a>',
            reverse("admin:msgs_supportgroupmessagecomment_history", args=[obj.pk]),
        )

    def text_excerpt(self, object):
        return truncatechars(object.text, 20)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SupportGroupMessage)
class SupportGroupMessageAdmin(MessageAdminMixin, VersionAdmin):
    fields = (
        "id",
        "created",
        "modified",
        "author_link",
        "group",
        "text",
        "image",
        "event",
        "required_membership_type",
        "readonly",
        "is_locked",
        "deleted",
    )
    readonly_fields = (
        "id",
        "author_link",
        "group",
        "text",
        "image",
        "event",
        "required_membership_type",
        "created",
        "modified",
    )
    list_display = (
        "id",
        "deleted",
        "author_link",
        "group",
        "text_preview",
        "event",
        "required_membership_type",
        "created",
        "comment_count",
        "report_count",
        "readonly",
        "is_locked",
    )
    search_fields = ("=id", "subject", "supportgroup__name", "author__search")
    list_filter = (
        AuthorFilter,
        MessageSupportGroupFilter,
        "supportgroup__type",
        RequiredMembershipListFilter,
        ReportListFilter,
        "deleted",
        "readonly",
    )

    inlines = [
        InlineSupportGroupMessageCommentAdmin,
    ]

    @admin.display(description="Nombre de commentaires")
    def comment_count(self, obj):
        count = SupportGroupMessageComment.objects.filter(message=obj.pk).count()
        if count == 0:
            return "-"

        return format_html(
            "<strong>{}</strong> " "<a href={}>(voir les commentaires)</a>",
            count,
            admin_url(
                "admin:msgs_supportgroupmessagecomment_changelist",
                query={"message_id": str(obj.id)},
            ),
        )

    @admin.display(description="Événement")
    def event(self, obj):
        return display_link(obj.linked_event)

    @admin.display(description="Groupe")
    def group(self, obj):
        return display_link(obj.supportgroup)

    class Media:
        pass


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

    @admin.display(description="Objet du signalement")
    def reported_object_link(self, obj):
        return display_link(obj.reported_object)

    @admin.display(description="Auteur·ice du signalement")
    def reported_object_author(self, obj):
        if not obj.reported_object:
            return "-"

        return display_link(obj.reported_object.author)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
