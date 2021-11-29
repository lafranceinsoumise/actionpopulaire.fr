from django.http import StreamingHttpResponse
from django.utils import timezone

from agir.people.actions.export import people_to_csv_lines

PERSON_EXPORT_LIMIT = 500


def export_people_to_csv(modeladmin, request, queryset):
    people = queryset[:PERSON_EXPORT_LIMIT]
    streaming_content = people_to_csv_lines(people)
    response = StreamingHttpResponse(
        streaming_content=streaming_content, content_type="text/csv"
    )

    response["Content-Disposition"] = "inline; filename=export_personnes_{}.csv".format(
        timezone.now()
        .astimezone(timezone.get_default_timezone())
        .strftime("%Y%m%d_%H%M")
    )

    return response


export_people_to_csv.short_description = (
    f"Exporter les personnes en CSV (max. {PERSON_EXPORT_LIMIT} personnnes par export)"
)
export_people_to_csv.allowed_permissions = ["export"]
