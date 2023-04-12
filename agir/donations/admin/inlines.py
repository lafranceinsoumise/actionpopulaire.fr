from django.contrib import admin

from agir.donations.models import (
    Document,
)


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    can_delete = False
