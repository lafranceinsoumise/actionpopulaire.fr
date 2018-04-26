from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import ugettext as _

from api.admin import admin_site

from polls.models import Poll, PollOption
from lib.utils import front_url


class PollOptionInline(admin.TabularInline):
    model = PollOption
    extra = 1

@admin.register(Poll, site=admin_site)
class PollAdmin(admin.ModelAdmin):
    inlines = [PollOptionInline]

    fields = ['title', 'link', 'description', 'start', 'end', 'rules', 'tags']
    readonly_fields = ['link']

    def link(self, object):
        if object.pk:
            return format_html(
                '<a href="{url}">{text}</a>',
                url=front_url('participate_poll', args=[object.pk]),
                text=_("Voir la consultation")
            )
