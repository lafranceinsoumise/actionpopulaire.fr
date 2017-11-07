from api.admin import admin_site
from django.contrib import admin

from polls.models import Poll, PollOption


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1

@admin.register(Poll, site=admin_site)
class PollAdmin(admin.ModelAdmin):
    inlines = [PollOptionInline]
