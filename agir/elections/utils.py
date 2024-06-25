from iso8601 import iso8601

from agir.elections.data import polling_station_dataframe
from agir.events.models import Event
from agir.lib.utils import replace_datetime_timezone

OVERSEAS_AND_AMERICAS = (
    "AR",
    "BL",
    "BO",
    "BR",
    "CA",
    "CL",
    "CO",
    "CR",
    "CU",
    "DO",
    "EC",
    "GF",
    "GP",
    "GT",
    "HN",
    "HT",
    "JM",
    "LC",
    "MF",
    "MQ",
    "MX",
    "NI",
    "PA",
    "PE",
    "PF",
    "PM",
    "PY",
    "SV",
    "TT",
    "US",
    "UY",
    "VE",
)

TREVE_ELECTORALE = {
    "OVERSEAS_AND_AMERICAS": [
        (iso8601.parse_date(start), iso8601.parse_date(end), *rest)
        for (start, end, *rest) in [
            # Législatives 2024
            (
                "2024-06-28 00:00:00Z",  # Start date
                "2024-06-29 20:00:00Z",  # End date
                (
                    "soiree-electorale",
                    "depart-commun",
                    "soutien",
                    "formations",
                    "reunion-groupe",
                    "reunion-boucle-departementale",
                ),  # Authorized event subtypes
            ),
            (
                "2024-07-05 00:00:00Z",  # Start date
                "2024-07-06 20:00:00Z",  # End date
                (
                    "soiree-electorale",
                    "depart-commun",
                    "soutien",
                    "formations",
                    "reunion-groupe",
                    "reunion-boucle-departementale",
                ),  # Authorized event subtypes
            ),
        ]
    ],
    "DEFAULT": [
        (iso8601.parse_date(start), iso8601.parse_date(end), *rest)
        for (start, end, *rest) in [
            (
                "2024-06-29 00:00:00+0200",  # Start date
                "2024-06-30 20:00:00+0200",  # End date
                (
                    "soiree-electorale",
                    "depart-commun",
                    "soutien",
                    "formations",
                    "reunion-groupe",
                    "reunion-boucle-departementale",
                ),  # Authorized event subtypes
            ),
            (
                "2024-07-06 00:00:00+0200",  # Start date
                "2024-07-07 20:00:00+0200",  # End date
                (
                    "soiree-electorale",
                    "depart-commun",
                    "soutien",
                    "formations",
                    "reunion-groupe",
                    "reunion-boucle-departementale",
                ),  # Authorized event subtypes
            ),
        ]
    ],
}


def get_treve_event_rules(event):
    is_overseas_and_americas = (
        event.location_country and event.location_country.code in OVERSEAS_AND_AMERICAS
    )

    if not is_overseas_and_americas:
        return TREVE_ELECTORALE["DEFAULT"]

    return [
        (
            replace_datetime_timezone(treve_start, event.timezone),
            replace_datetime_timezone(treve_end, event.timezone),
            authorized_subtype_labels,
        )
        for (
            treve_start,
            treve_end,
            authorized_subtype_labels,
        ) in TREVE_ELECTORALE["OVERSEAS_AND_AMERICAS"]
    ]


def is_forbidden_during_treve_event(event_data):
    event_pk = event_data.get("id", None)

    if event_pk:
        event = Event.objects.get(pk=event_pk)
        start_time = event_data.get("start_time", event.start_time)
        end_time = event_data.get("end_time", event.end_time)
        subtype = event_data.get("subtype", event.subtype)
        country = event_data.get("location_country", event.location_country)
        timezone = event_data.get("timezone", event.timezone)
    else:
        start_time = event_data.get("start_time", None)
        end_time = event_data.get("end_time", None)
        subtype = event_data.get("subtype", None)
        country = event_data.get("location_country", None)
        timezone = event_data.get("timezone", None)

    event = Event(
        start_time=start_time,
        end_time=end_time,
        subtype=subtype,
        location_country=country,
        timezone=timezone,
    )

    for treve_start, treve_end, authorized_subtype_labels in get_treve_event_rules(
        event
    ):
        if event.start_time is None or event.end_time is None:
            return True

        if (
            authorized_subtype_labels
            and event.subtype
            and event.subtype.label in authorized_subtype_labels
        ):
            continue

        if (
            treve_start <= event.start_time < treve_end
            or treve_start <= event.end_time < treve_end
        ):
            return True

    return False


def get_polling_station(polling_station_id=""):
    if not polling_station_id:
        return None

    data = polling_station_dataframe
    polling_station = data.loc[data.id_brut_insee == polling_station_id].to_dict(
        "records"
    )

    return polling_station[0] if polling_station else None


def get_polling_station_label(polling_station=None, fallback=""):
    if isinstance(polling_station, str):
        polling_station = get_polling_station(polling_station)

    if polling_station is None:
        return fallback

    libelle = str(polling_station.get("libelle_reu", "")).upper()
    label = f"{str(polling_station['code']).upper()} - {libelle}"

    address = " ".join(
        [
            str(polling_station.get("num_voie_reu", "")).upper(),
            str(polling_station.get("voie_reu", "")).upper(),
        ]
    )
    address = " ".join(address.split())

    if address:
        label = f"{label} - {address}"

    if polling_station.get("circonscription", ""):
        label = f"{label} ({polling_station['circonscription']})"

    return label


def get_polling_station_circonscription(polling_station=None, fallback=""):
    if isinstance(polling_station, str):
        polling_station = get_polling_station(polling_station)

    if polling_station is None:
        return fallback

    return polling_station.get("circonscription", fallback)
