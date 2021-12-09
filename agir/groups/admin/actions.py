from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.translation import gettext as _

from ..actions import groups_to_csv_lines


def export_groups(modeladmin, request, queryset):
    response = StreamingHttpResponse(
        groups_to_csv_lines(queryset), content_type="text/csv"
    )
    response["Content-Disposition"] = "inline; filename=export_groups_{}.csv".format(
        timezone.now()
        .astimezone(timezone.get_default_timezone())
        .strftime("%Y%m%d_%H%M")
    )

    return response


export_groups.short_description = _("Exporter les groupes en CSV")


def make_published(modeladmin, request, queryset):
    queryset.update(published=True)


make_published.short_description = _("Publier les groupes")


def unpublish(modeladmin, request, queryset):
    queryset.update(published=False)


unpublish.short_description = _("Dépublier les groupes")
