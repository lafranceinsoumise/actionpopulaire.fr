import datetime
import string

from django.template.defaultfilters import floatformat
from django.utils.html import format_html, format_html_join, mark_safe
from django.utils.formats import date_format
from django.utils.timezone import utc, is_aware
from django.utils.translation import ugettext as _, ngettext


def display_address(object):
    parts = []
    if getattr(object, "location_name", None):
        parts.append(format_html("<em>{}</em>", object.location_name))

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
    return "{}\u00A0€".format(floatformat(price / 100, 2))


def pretty_time_since(d, relative_to=None):
    """ Convert datetime.date to datetime.datetime for comparison."""
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if relative_to and not isinstance(relative_to, datetime.datetime):
        relative_to = datetime.datetime(
            relative_to.year, relative_to.month, relative_to.day
        )

    relative_to = relative_to or datetime.datetime.now(utc if is_aware(d) else None)

    delta = relative_to - d
    delta_seconds = delta.days * 24 * 3600 + delta.seconds

    if delta.days > 365 and d.year != relative_to.year and d.month != relative_to.month:
        return _("en {:d} ou avant").format(d.year)
    elif delta.days > 30 and (d.month != relative_to.month):
        return _("en {} dernier").format(date_format(d, "F"))
    elif delta.days > 14:
        return _("il y a {:d} semaines").format(round(delta.days / 7))
    elif delta.days > 0 and d.day == relative_to.day - 1:
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


def str_summary(text, length_max=500, last_word_limit=100):
    """ limite un message en taille.

    Le message n'est pas coupé en plein milieu d'un mot, sauf si ce mot est plus long que `last_word_limit`
    '...' est ajouté à la fin de la chaîne."""
    text_len = len(text)
    if text_len > length_max:
        n = min(text_len, length_max)
        m = 0
        while text[n] not in string.whitespace and m <= last_word_limit:
            n -= 1
            m += 1
        text = text[0 : n + 1]
        if text_len > length_max:
            text += "..."
    return text
