from operator import attrgetter

from django.http import StreamingHttpResponse
from django.urls import reverse
from django.utils import timezone

from agir.api import settings
from agir.lib.export import dicts_to_csv_lines

COMMON_FIELDS = [
    "id",
    "first_name",
    "last_name",
    "is_insoumise",
    "is_2022",
    "email",
    "contact_phone",
    "location_zip",
    "location_city",
    "location_country",
    "created",
]

ADDRESS_FIELDS = [
    "location_name",
    "location_address1",
    "location_address2",
    "location_zip",
    "location_city",
    "location_country",
]
FIELDS = COMMON_FIELDS + ["address", "admin_link"]

common_extractor = attrgetter(*COMMON_FIELDS)
address_parts_extractor = attrgetter(*ADDRESS_FIELDS)


def people_to_csv_lines(queryset):
    return dicts_to_csv_lines(people_to_dicts(queryset), fieldnames=FIELDS)


def people_to_dicts(queryset):
    for person in queryset.iterator():
        person_dict = {
            k: str(v) for k, v in zip(COMMON_FIELDS, common_extractor(person))
        }
        person_dict["address"] = "\n".join(
            str(component) for component in address_parts_extractor(person) if component
        )
        person_dict["admin_link"] = settings.API_DOMAIN + reverse(
            "admin:people_person_change", args=[person.id]
        )

        yield person_dict


def people_to_csv_response(people):
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
