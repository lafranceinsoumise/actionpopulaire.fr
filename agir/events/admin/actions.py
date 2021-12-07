from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from agir.events.models import Event
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
    queryset.update(visibility=Event.VISIBILITY_PUBLIC)


make_published.short_description = _("Passer les événements en visibilité publique")


def make_private(modeladmin, request, queryset):
    queryset.update(visibility=Event.VISIBILITY_ORGANIZER)


make_private.short_description = _(
    "Passer les événements en visibilité organisateurices"
)


def unpublish(modeladmin, request, queryset):
    queryset.update(visibility=Event.VISIBILITY_ADMIN)


unpublish.short_description = _(
    "Passer les événements en visibilité administrateurices"
)
