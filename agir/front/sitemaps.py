from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from agir.municipales.models import CommunePage
from ..events.models import Event
from ..groups.models import SupportGroup


class EventSitemap(Sitemap):
    changefreq = "always"

    def items(self):
        return Event.objects.listed()

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


class CommunesSitemap(Sitemap):
    changefreq = "always"

    def items(self):
        return CommunePage.objects.filter(published=True)

    def location(self, c):
        return reverse(
            "view_commune",
            kwargs={"code_departement": c.code_departement, "slug": c.slug},
        )

    def lastmod(self, c):
        return c.modified


sitemaps = {
    "events": EventSitemap,
    "groups": SupportGroupSitemap,
    "communes": CommunesSitemap,
}
