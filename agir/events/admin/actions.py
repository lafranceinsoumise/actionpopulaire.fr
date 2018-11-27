from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from ..actions import events_to_csv_lines


def export_events(modeladmin, request, queryset):
    response = StreamingHttpResponse(
        events_to_csv_lines(queryset), content_type="text/csv"
    )
    response["Content-Disposition"] = "inline; filename=export_events_{}.csv".format(
        timezone.now()
        .astimezone(timezone.get_default_timezone())
        .strftime("%Y%m%d_%H%M")
    )

    return response


export_events.short_description = _("Exporter les événements en CSV")


def make_published(modeladmin, request, queryset):
    queryset.update(published=True)


make_published.short_description = _("Publier les événements")


def unpublish(modeladmin, request, queryset):
    queryset.update(published=False)


unpublish.short_description = _("Dépublier les événements")
