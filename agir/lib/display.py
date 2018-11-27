import datetime

from django.template.defaultfilters import floatformat
from django.utils.html import format_html, format_html_join, mark_safe
from django.utils.formats import date_format
from django.utils.timezone import utc, is_aware
from django.utils.translation import ugettext as _, ngettext


def display_address(object):
    parts = []
    if getattr(object, "location_name", None):
        parts.append(format_html("<strong>{}</strong>", object.location_name))

    if object.location_address1:
        parts.append(object.location_address1)
        if object.location_address2:
            parts.append(object.location_address2)
    elif object.location_address:
        # use full address (copied from NationBuilder) only when we have no address1 field
        parts.append(object.location_address)

    if object.location_state:
        parts.append(object.location_state)

    if object.location_zip and object.location_city:
        parts.append("{} {}".format(object.location_zip, object.location_city))
    else:
        if object.location_zip:
            parts.append(object.location_zip)
        if object.location_city:
            parts.append(object.location_city)

    if object.location_country and str(object.location_country) != "FR":
        parts.append(object.location_country.name)

    return format_html_join(mark_safe("<br/>"), "{}", ((part,) for part in parts))


def display_price(price):
    return "{} €".format(floatformat(price / 100, 2))


def pretty_time_since(d, now=None):
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    now = now or datetime.datetime.now(utc if is_aware(d) else None)

    delta = now - d
    delta_seconds = delta.days * 24 * 3600 + delta.seconds

    if delta.days > 365 and d.year != now.year and d.month != now.month:
        return _("en {:d}").format(d.year)
    elif delta.days > 30 and (d.month != now.month):
        return _("en {} dernier").format(date_format(d, "F"))
    elif delta.days > 14:
        return _("il y a {:d} semaines").format(round(delta.days / 7))
    elif delta.days > 0 and d.day == now.day - 1:
        return _("hier")
    elif delta.days > 0:
        num_days = round(delta_seconds / 3600 / 24)
        return ngettext("il y a %d jour", "il y a %d jours", num_days) % num_days
    elif delta_seconds > 3600:
        num_hours = round(delta_seconds / 3600)
        return ngettext("il y a %d heure", "il y a %d heures", num_hours) % num_hours
    elif delta_seconds > 60:
        num_seconds = round(delta_seconds / 60)
        return (
            ngettext("il y a %d minute", "il y a %d minutes", num_seconds) % num_seconds
        )
    else:
        return _("Il y a moins d'une minute")
