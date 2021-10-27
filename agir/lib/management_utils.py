from argparse import ArgumentTypeError
from datetime import date, time

import phonenumbers
import re
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance as DistanceMeasure
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from phonenumbers import NumberParseException

SEP = r"[/-]"

date_regex_le = re.compile(
    r"^(?P<day>\d{2})" + SEP + r"(?P<month>\d{2})" + SEP + r"(?P<year>\d{4})$"
)

date_regex_be = re.compile(
    r"^(?P<year>\d{4})" + SEP + r"(?P<month>\d{2})" + SEP + r"(?P<day>\d{2})$"
)

datetime_regex = re.compile(
    r"^" + r"(?P<year>\d{4})" + SEP + r"(?P<month>\d{2})" + SEP + r"(?P<day>\d{2})"
    r"\s+"
    r"(?P<hour>\d{2})"
    r":"
    r"(?P<minute>\d{2})"
    r"(?::(?P<second>\d{2}))?"
    r"$"
)


month_regexp_be = re.compile(r"^(?P<year>[0-9]{4})[/-](?P<month>[0-9]{2})$")
month_regexp_le = re.compile(r"^(?P<month>[0-9]{2})[-/](?P<year>[0-9]{4})$")


def date_argument(d: str) -> date:
    m = date_regex_le.match(d)

    if m is None:
        m = date_regex_be.match(d)

    if m is None:
        raise ArgumentTypeError(f"'{d}'' doit être de la forme 'AAAA-MM-DD'.")

    return date(int(m.group("year")), int(m.group("month")), int(m.group("day")))


def date_as_local_datetime_argument(d: str) -> timezone.datetime:
    d = date_argument(d)
    return timezone.make_aware(timezone.datetime.combine(d, time()))


def datetime_argument(d):
    m = datetime_regex.match(d)

    if m is None:
        raise ArgumentTypeError(f"'{d}' doit être de la form 'AAAA-MM-DD hh:mm'")

    return timezone.make_aware(
        timezone.datetime(
            year=int(m.group("year")),
            month=int(m.group("month")),
            day=int(m.group("day")),
            hour=int(m.group("hour")),
            minute=int(m.group("minute")),
            second=int(m.group("second") or 0),
        )
    )


def email_argument(email):
    try:
        validate_email(email)
    except ValidationError:
        raise ArgumentTypeError(f"'{email}' n'est pas une adresse email valide.")
    return email


def month_range(year, month, tz=None):
    first_day = timezone.make_aware(timezone.datetime(year, month, 1), tz)

    if month == 12:
        return (first_day, first_day.replace(day=31))
    return (first_day, first_day.replace(month=month + 1) - timezone.timedelta(days=1))


def month_argument(arg: str):
    match = month_regexp_be.match(arg) or month_regexp_le.match(arg)

    if match is None:
        raise ArgumentTypeError(f"'{arg}'' doit être de la forme 'AAAA-MM'.")

    return month_range(int(match.group("year")), int(match.group("month")))


def distance_argument(d):
    m = re.match("^([0-9.]+)([a-zA-Z]+)$", d)

    if not m:
        raise ArgumentTypeError(f"{d} n'est pas une mesure de distance correcte")

    return DistanceMeasure(**{m.group(2): float(m.group(1))})


def event_argument(event_id):
    from agir.events.models import Event

    try:
        return Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise ArgumentTypeError("Cet événement n'existe pas.")


def coordinates_argument(coords):
    lon, lat = map(str.strip, coords.split(","))
    return Point(float(lon), float(lat), srid=4326)


def departement_argument(dep):
    from agir.lib.data import filtre_departement

    return filtre_departement(dep)


def region_argument(reg):
    from agir.lib.data import filtre_region

    return filtre_region(reg)


def segment_argument(segment_id):
    from agir.mailing.models import Segment

    try:
        return Segment.objects.get(pk=segment_id)
    except Segment.DoesNotExist:
        raise ValueError("Ce segment n'existe pas.")


def phone_argument(phone_number):
    try:
        number = phonenumbers.parse(phone_number, None)
    except NumberParseException:
        raise ArgumentTypeError(f" '{phone_number}' n'est pas un numéro de téléphone.")

    if not phonenumbers.is_valid_number(number):
        raise ArgumentTypeError(
            f"'{phone_number}' n'est pas un numéro de téléphone attribuable."
        )

    return number
