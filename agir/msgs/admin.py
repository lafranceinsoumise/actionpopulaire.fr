from django.contrib import admin
from django.contrib.admin.options import TabularInline
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html
from reversion.admin import VersionAdmin

from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment, UserReport


@admin.register(SupportGroupMessageComment)
class SupportGroupMessageCommentAdmin(VersionAdmin):
    fields = ("created", "modified", "author", "text", "image", "msg", "deleted")
    readonly_fields = ("created", "modified", "author", "text", "image", "msg")
    list_display = ("text_excerpt", "author", "msg", "created", "deleted")
    list_filter = ("deleted",)
    model = SupportGroupMessageComment

    def text_excerpt(self, object):
        return truncatechars(object.text, 20)

    text_excerpt.short_description = "Texte"

    def msg(self, object):
        href = reverse(
            "admin:msgs_supportgroupmessage_change", args=[object.message.pk],
        )
        return format_html(f'<a href="{href}">{object.message.pk}</a>')

    msg.short_description = "Message initial"

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class InlineSupportGroupMessageCommentAdmin(TabularInline):
    fields = ("created", "modified", "author", "text", "image", "history", "deleted")
    readonly_fields = ("created", "modified", "author", "text", "image", "history")
    model = SupportGroupMessageComment

    def history(self, object):
        return format_html(
            '<a href="{}">Historique</a>',
            reverse("admin:msgs_supportgroupmessagecomment_history", args=[object.pk]),
        )

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
        "created",
        "supportgroup",
        "linked_event",
        "comment_count",
        "deleted",
    )
    list_filter = ("deleted",)
    inlines = [
        InlineSupportGroupMessageCommentAdmin,
    ]

    def text_excerpt(self, object):
        return truncatechars(object.text, 20)

    text_excerpt.short_description = "Texte"

    def comment_count(self, object):
        return SupportGroupMessageComment.objects.filter(message=object.pk).count()

    comment_count.short_description = "Nombre de commentaires"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    fields = ("reporter", "reported_object_link", "created")
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

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
