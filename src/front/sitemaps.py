from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from events.models import Event
from groups.models import SupportGroup


class EventSitemap(Sitemap):
    changefreq = 'always'

    def items(self):
        return Event.objects.published()

    def location(self, obj):
        return reverse('view_event', args=[obj.id])

    def lastmod(self, obj):
        return obj.created


class SupportGroupSitemap(Sitemap):
    changefreq = 'always'

    def items(self):
        return SupportGroup.active.all()

    def location(self, obj):
        return reverse('view_group', args=[obj.id])

    def lastmod(self, obj):
        return obj.created


sitemaps = {
    'events': EventSitemap,
    'groups': SupportGroupSitemap,
}