from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from agir.lib.admin.utils import display_link, admin_url


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
        is_comment = hasattr(obj, "message")
        message = obj.message if is_comment else obj

        return format_html(
            "<details style='width:240px;' {}>"
            "<summary style='cursor:pointer;overflow:hidden;text-overflow:ellipsis;'><strong>{}</strong></summary>"
            "<blockquote>{}</blockquote>"
            "</details>",
            "open" if is_comment else "",
            mark_safe(message.subject if message.subject else "-"),
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
