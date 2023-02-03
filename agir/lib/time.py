from datetime import datetime, timedelta, date
import re

from django.utils import timezone


def get_datetime_part_from_string(datetime_part, string):
    """Return either a matched number or 0."""
    pattern = r"(\d*) " + re.escape(datetime_part)
    matches = re.findall(pattern, string)
    if matches:
        return int(matches[0])
    return 0


def dehumanize_naturaltime(text, now=None):
    """
    Convert a naturaltime string to a datetime object.
    cf. https://github.com/jamiebull1/dehumanize
    """
    if isinstance(text, date):
        # datetime is a subclass of date
        return text

    text = text.lower().strip()
    if not now:
        now = timezone.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if text == "now":
        return now
    if text == "today":
        return today
    if text == "yesterday":
        return today - timedelta(days=1)
    if text == "tomorrow":
        return today + timedelta(days=1)

    if "ago" in text:
        multiplier = -1
    elif "from now" in text:
        multiplier = 1
    else:
        raise ValueError("%s is not a valid naturaltime" % text)

    text = text.replace("an ", "1 ")
    text = text.replace("a ", "1 ")

    years = get_datetime_part_from_string("year", text)
    months = get_datetime_part_from_string("month", text)
    weeks = get_datetime_part_from_string("week", text)
    days = get_datetime_part_from_string("day", text)
    days = days + weeks * 7 + months * 30 + years * 365

    hours = get_datetime_part_from_string("hour", text)
    minutes = get_datetime_part_from_string("minute", text)
    seconds = get_datetime_part_from_string("second", text)
    delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    delta *= multiplier

    return now + delta
