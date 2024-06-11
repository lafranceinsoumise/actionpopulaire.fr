from collections import OrderedDict
from operator import attrgetter

from django.http import StreamingHttpResponse
from django.utils import timezone

from agir.lib.export import dicts_to_csv_lines

VOTER_FIELD = OrderedDict(
    {
        "id": "id",
        "first_name": "prenom",
        "last_name": "nom",
        "email": "email",
        "contact_phone": "telephone",
        "commune": "commune",
        "consulate": "consulat",
        "polling_station_label": "bureau_de_vote",
        "voter_id": "numero_national_electeur",
        "status": "statut",
        "created": "date_de_creation",
    }
)

VOTING_PROXY_REQUEST_FIELD = OrderedDict(
    {
        **VOTER_FIELD,
        "voting_date": "date_de_scrutin",
        "proxy": "volontaire",
    }
)
voting_proxy_requests_extractor = attrgetter(*VOTING_PROXY_REQUEST_FIELD.keys())


def stream_csv_response(streaming_content, file_prefix=""):
    response = StreamingHttpResponse(
        streaming_content=streaming_content, content_type="text/csv"
    )
    ts = (
        timezone.now()
        .astimezone(timezone.get_default_timezone())
        .strftime("%Y%m%d_%H%M")
    )
    response["Content-Disposition"] = f"inline; filename={file_prefix}_{ts}.csv"

    return response


def voting_proxy_requests_to_dicts(queryset):
    for voting_proxy_requests in queryset.iterator():
        voting_proxy_requests_dict = {
            k: str(v)
            for k, v in zip(
                VOTING_PROXY_REQUEST_FIELD.values(),
                voting_proxy_requests_extractor(voting_proxy_requests),
            )
        }
        yield voting_proxy_requests_dict


def voting_proxy_requests_to_csv_response(voting_proxy_requestss):
    streaming_content = dicts_to_csv_lines(
        voting_proxy_requests_to_dicts(voting_proxy_requestss),
        fieldnames=VOTING_PROXY_REQUEST_FIELD.values(),
    )
    return stream_csv_response(
        streaming_content, file_prefix="export_demandes_procuration"
    )


VOTING_PROXY_FIELD = OrderedDict(
    {
        **VOTER_FIELD,
        "date_of_birth": "date_de_naissance",
        "available_voting_dates": "disponibilté",
        "remarks": "remarques",
        "person": "personne_AP",
    }
)
voting_proxies_extractor = attrgetter(*VOTING_PROXY_FIELD.keys())


def voting_proxies_to_dicts(queryset):
    for voting_proxies in queryset.iterator():
        voting_proxies_dict = {
            k: str(v)
            for k, v in zip(
                VOTING_PROXY_FIELD.values(),
                voting_proxies_extractor(voting_proxies),
            )
        }
        yield voting_proxies_dict


def voting_proxies_to_csv_response(voting_proxy_requestss):
    streaming_content = dicts_to_csv_lines(
        voting_proxies_to_dicts(voting_proxy_requestss),
        fieldnames=VOTING_PROXY_FIELD.values(),
    )
    return stream_csv_response(
        streaming_content, file_prefix="export_volontaires_procuration"
    )
