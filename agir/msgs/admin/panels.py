from django.contrib import admin
from django.urls import path
from django.utils.html import format_html, format_html_join
from reversion.admin import VersionAdmin

from agir.lib.admin.utils import display_link, admin_url
from agir.msgs.admin import filters
from agir.msgs.admin.inlines import InlineSupportGroupMessageCommentAdmin
from agir.msgs.admin.mixins import MessageAdminMixin
from agir.msgs.admin.views import CreateAndSendSupportGroupMessageView
from agir.msgs.models import SupportGroupMessage, SupportGroupMessageComment, UserReport


@admin.register(SupportGroupMessageComment)
class SupportGroupMessageCommentAdmin(MessageAdminMixin, VersionAdmin):
    fields = (
        "id",
        "created",
        "modified",
        "author_link",
        "message_link",
        "text",
        "attachment_display",
        "deleted",
    )
    readonly_fields = (
        "id",
        "author_link",
        "message_link",
        "text",
        "attachment_display",
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
    list_filter = (
        filters.AuthorFilter,
        filters.CommentSupportGroupFilter,
        filters.ReportListFilter,
        "deleted",
    )
    search_fields = ("=id", "=message__id", "message__subject", "author__search")
    model = SupportGroupMessageComment

    @admin.display(description="Message")
    def message_link(self, obj):
        return display_link(obj.message, obj.message.pk)


@admin.register(SupportGroupMessage)
class SupportGroupMessageAdmin(MessageAdminMixin, VersionAdmin):
    ordering = ("-created",)
    fields = (
        "id",
        "created",
        "modified",
        "author_link",
        "group",
        "text",
        "event",
        "attachment_display",
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
        "event",
        "attachment_display",
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
        filters.AuthorFilter,
        filters.MessageSupportGroupFilter,
        "supportgroup__type",
        filters.RequiredMembershipListFilter,
        filters.ReportListFilter,
        "deleted",
        "readonly",
    )

    inlines = (InlineSupportGroupMessageCommentAdmin,)

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

    def get_urls(self):
        return [
            path(
                "send/",
                self.admin_site.admin_view(
                    CreateAndSendSupportGroupMessageView.as_view(model_admin=self)
                ),
                name="{}_{}_send".format(self.opts.app_label, self.opts.model_name),
            )
        ] + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(
            {
                "has_send_link": request.user.has_perm("msgs.send_supportgroupmessage"),
                "send_link": f'{admin_url("admin:{}_{}_send".format(self.opts.app_label, self.opts.model_name))}',
            }
        )

        return super().changelist_view(request, extra_context)

    class Media:
        pass


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    fields = readonly_fields = (
        "reporter_link",
        "created",
        "reported_object_link",
        "reported_object_author",
        "reported_object_text",
    )
    list_display = (
        "__str__",
        "created",
        "reporter_link",
        "reported_object_author",
        "reported_object_link",
        "reported_object_deleted",
    )
    search_fields = ("reporter__search", "=object_id")

    @admin.display(description="Auteur·ice du signalement", ordering="reporter")
    def reporter_link(self, obj):
        return display_link(obj.reporter)

    @admin.display(description="Objet du signalement")
    def reported_object_link(self, obj):
        return display_link(
            obj.reported_object, f"{obj.content_type.name} ({obj.reported_object.id})"
        )

    @admin.display(description="Texte")
    def reported_object_text(self, obj):
        if not obj.reported_object:
            return "-"

        message = (
            obj.reported_object.message
            if hasattr(obj.reported_object, "message")
            else obj.reported_object
        )

        selected_style = "background-color:red;color:white;font-weight:600;font-size:1.5em;padding:24px;"
        messages = format_html_join(
            "",
            """
            <figure style="width:100%;padding:0;margin:4px 0;">
                <figcaption style="padding:0 8px;"><strong>{}</strong></figcaption>
                <blockquote style="margin:0;padding:0;border:none;">
                    <p style="padding:16px;background-color:#eee;border-radius:8px;{}">{}</p>
                </blockquote>
                <figcaption style="padding:0 8px;text-align:right;"><em>{}</em></figcaption>
            </figure>
            """,
            [
                (
                    str(message.author),
                    selected_style if message == obj.reported_object else "",
                    message.text,
                    message.created.strftime("%d/%m/%Y à %H:%M"),
                )
                for message in [message, *message.comments.all()]
            ],
        )

        return format_html(
            """
            <details open>
                <summary style='cursor:pointer;overflow:hidden;text-overflow:ellipsis;'>
                    <strong>{}</strong>
                </summary>
                {}
            </details>
            """,
            message.subject if message.subject else "-",
            messages,
        )

    @admin.display(description="Auteur·ice de l'objet")
    def reported_object_author(self, obj):
        if not obj.reported_object:
            return "-"

        return display_link(obj.reported_object.author)

    @admin.display(description="Auteur·ice de l'objet")
    def reported_object_author(self, obj):
        if not obj.reported_object:
            return "-"

        return display_link(obj.reported_object.author)

    @admin.display(description="Objet supprimé", boolean=True)
    def reported_object_deleted(self, obj):
        return obj and obj.reported_object and obj.reported_object.deleted

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
