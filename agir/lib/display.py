from django.template.defaultfilters import floatformat
from django.utils.html import format_html, format_html_join, mark_safe


def display_address(object):
    parts = []
    if getattr(object, 'location_name', None):
        parts.append(format_html('<strong>{}</strong>', object.location_name))

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
        parts.append('{} {}'.format(object.location_zip, object.location_city))
    else:
        if object.location_zip:
            parts.append(object.location_zip)
        if object.location_city:
            parts.append(object.location_city)

    if object.location_country and str(object.location_country) != 'FR':
        parts.append(object.location_country.name)

    return format_html_join(mark_safe('<br/>'), '{}', ((part,) for part in parts))


def display_price(price):
    return "{} €".format(floatformat(price / 100, 2))
