from collections import OrderedDict
from operator import attrgetter

from glom import glom, Iter

from django.http import StreamingHttpResponse
from django.utils import timezone

from agir.lib.admin.utils import admin_url
from agir.lib.export import dicts_to_csv_lines

COMMON_FIELDS = (
    "id",
    "first_name",
    "last_name",
    "is_political_support",
    "email",
    "contact_phone",
    "location_zip",
    "location_city",
    "location_country",
    "created",
)

ADDRESS_FIELDS = (
    "location_name",
    "location_address1",
    "location_address2",
    "location_zip",
    "location_city",
    "location_country",
)
PERSON_FIELDS = COMMON_FIELDS + ("address", "admin_link")


def address(p):
    return "\n".join(str(getattr(p, c)) for c in ADDRESS_FIELDS if getattr(p, c))


def lien_admin(p):
    return admin_url("people_person_change", args=(p.id,), absolute=True)


spec = {**{f: f for f in COMMON_FIELDS}, "address": address, "admin_link": lien_admin}


def people_to_csv_lines(queryset):
    return dicts_to_csv_lines(people_to_dicts(queryset), fieldnames=PERSON_FIELDS)


def people_to_dicts(queryset):
    return glom(
        queryset,
        Iter(spec),
    )


def stream_csv_response(streaming_content):
    response = StreamingHttpResponse(
        streaming_content=streaming_content, content_type="text/csv"
    )
    response["Content-Disposition"] = "inline; filename=export_personnes_{}.csv".format(
        timezone.now()
        .astimezone(timezone.get_default_timezone())
        .strftime("%Y%m%d_%H%M")
    )

    return response


def people_to_csv_response(people):
    streaming_content = people_to_csv_lines(people)
    return stream_csv_response(streaming_content)


LIAISON_FIELDS = OrderedDict(
    {
        "id": "id",
        "first_name": "prenom",
        "last_name": "nom",
        "location_address1": "adresse",
        "location_address2": "complement_adresse",
        "location_zip": "code_postal",
        "location_city": "ville",
        "location_country": "pays",
    }
)
liaison_extractor = attrgetter(*LIAISON_FIELDS.keys())


def liaisons_to_dicts(queryset):
    for liaison in queryset.iterator():
        liaison_dict = {
            k: str(v)
            for k, v in zip(LIAISON_FIELDS.values(), liaison_extractor(liaison))
        }
        yield liaison_dict


def liaisons_to_csv_response(liaisons):
    streaming_content = dicts_to_csv_lines(
        liaisons_to_dicts(liaisons), fieldnames=LIAISON_FIELDS.values()
    )
    return stream_csv_response(streaming_content)
