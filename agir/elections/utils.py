from iso8601 import iso8601

from agir.events.models import Event

TREVE_ELECTORALE = [
    (iso8601.parse_date(start), iso8601.parse_date(end), *rest)
    for (start, end, *rest) in [
        # Européennes 2024
        (
            "2024-06-08 00:00:00+0200",  # Start date
            "2024-06-09 20:00:00+0200",  # End date
            (
                "GF",
                "GP",
                "MQ",
                "PF",
                "BL",
                "MF",
                "PM",
                "AR",
                "BO",
                "BR",
                "CA",
                "CL",
                "CO",
                "CR",
                "HN",
                "NI",
                "DO",
                "EC",
                "GT",
                "SV",
                "HT",
                "MX",
                "PA",
                "CU",
                "JM",
                "PE",
                "PY",
                "US",
                "UY",
                "VE",
                "LC",
                "TT",
            ),  # Limited to country codes
            (
                "soiree-electorale",
                "depart-commun",
                "soutien",
            ),  # Authorized event subtypes
        ),
        (
            "2024-06-08 00:00:00+0200",  # Start date
            "2024-06-09 20:00:00+0200",  # End date
            None,  # Limited to country codes
            (
                "soiree-electorale",
                "depart-commun",
                "soutien",
            ),  # Authorized event subtypes
        ),
    ]
]


def is_forbidden_during_treve_event(event_data):
    event_pk = event_data.get("id", None)
    if event_pk:
        event = Event.objects.get(pk=event_pk)
        start_time = event_data.get("start_time", event.start_time)
        end_time = event_data.get("end_time", event.end_time)
        subtype = event_data.get("subtype", event.subtype)
        country = event_data.get("location_country", event.location_country)
    else:
        start_time = event_data.get("start_time", None)
        end_time = event_data.get("end_time", None)
        subtype = event_data.get("subtype", None)
        country = event_data.get("location_country", None)

    event = Event(
        start_time=start_time,
        end_time=end_time,
        subtype=subtype,
        location_country=country,
    )

    for (
        treve_start,
        treve_end,
        country_codes,
        authorized_subtype_labels,
    ) in TREVE_ELECTORALE:
        if (
            country_codes
            and event.location_country
            and event.location_country.code not in country_codes
        ):
            continue
        if (
            authorized_subtype_labels
            and event.subtype
            and event.subtype.label in authorized_subtype_labels
        ):
            continue
        if event.start_time is None or event.end_time is None:
            return True
        if (
            treve_start <= event.start_time < treve_end
            or treve_start <= event.end_time < treve_end
        ):
            return True

    return False
