from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from ..events.models import Event
from ..groups.models import SupportGroup


class EventSitemap(Sitemap):
    changefreq = "always"

    def items(self):
        return Event.objects.published()

    def location(self, obj):
        return reverse("view_event", args=[obj.id])

    def lastmod(self, obj):
        return max(obj.modified, obj.end_time)


class SupportGroupSitemap(Sitemap):
    changefreq = "always"

    def items(self):
        return SupportGroup.objects.active().all()

    def location(self, obj):
        return reverse("view_group", args=[obj.id])

    def lastmod(self, obj):
        return obj.modified


sitemaps = {"events": EventSitemap, "groups": SupportGroupSitemap}
