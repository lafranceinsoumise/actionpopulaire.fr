from django.contrib import admin

from agir.donations.models import (
    Document,
)


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    can_delete = False
    ordering = ("-pk",)
    deleted = False

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted=self.deleted)


class DeletedDocumentInline(DocumentInline):
    verbose_name_plural = "Documents supprimés"
    exclude = ("deleted",)
    deleted = True

    def has_add_permission(self, request, obj):
        return False
