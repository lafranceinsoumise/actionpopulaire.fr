from django.contrib.admin.options import TabularInline
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.html import format_html

from agir.msgs.admin.mixins import MessageAdminMixin
from agir.msgs.models import SupportGroupMessageComment


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
