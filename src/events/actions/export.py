import csv
from operator import attrgetter
import bleach
from html import unescape
from django.utils.timezone import get_default_timezone


__all__ = ['event_queryset_to_csv']


COMMON_FIELDS = ['name', 'contact_email', 'contact_phone', 'description', 'start_time', 'end_time']

address_fields = ['location_name', 'location_address1', 'location_zip', 'location_city']

common_extractor = attrgetter(*COMMON_FIELDS)
address_parts_extractor = attrgetter(*address_fields)

initiator_extractor = attrgetter('first_name', 'last_name', 'contact_phone', 'email')

address_template = "{}, {}, {} {}"
initiator_template = "{} {} {} <{}>"


def event_queryset_to_csv(queryset, output, timezone=None):
    if timezone is None:
        timezone = get_default_timezone()

    w = csv.DictWriter(output, fieldnames=COMMON_FIELDS + ['address', 'animators'])
    w.writeheader()

    for e in queryset.prefetch_related('organizer_configs'):
        d = {k: v for k, v in zip(COMMON_FIELDS, common_extractor(e))}
        d['start_time'] = d['start_time'].astimezone(timezone).strftime('%d/%m %H:%M')
        d['end_time'] = d['end_time'].astimezone(timezone).strftime('%d/%m %H:%M')
        d['description'] = unescape(bleach.clean(d['description'].replace('<br />', '\n'), tags=[], strip=True))
        d['address'] = address_template.format(*address_parts_extractor(e))
        d['animators'] = ' / '.join(
            initiator_template.format(*initiator_extractor(og.person)).strip() for og in e.organizer_configs.all())
        w.writerow(d)
