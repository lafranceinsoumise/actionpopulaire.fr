import csv
from operator import attrgetter
import bleach
from html import unescape
from django.utils.timezone import get_default_timezone
from django.conf import settings
from django.urls import reverse

from front import urls as front_urls


__all__ = ['event_queryset_to_csv']


COMMON_FIELDS = ['name', 'contact_email', 'contact_phone', 'description', 'start_time', 'end_time']
ADRESS_FIELDS = ['location_name', 'location_address1', 'location_zip', 'location_city']
LINK_FIELDS = ['link', 'admin_link']

common_extractor = attrgetter(*COMMON_FIELDS)
address_parts_extractor = attrgetter(*ADRESS_FIELDS)

initiator_extractor = attrgetter('first_name', 'last_name', 'contact_phone', 'email')

address_template = "{}, {}, {} {}"
initiator_template = "{} {} {} <{}>"


def event_queryset_to_csv(queryset, output, timezone=None):
    if timezone is None:
        timezone = get_default_timezone()

    w = csv.DictWriter(output, fieldnames=COMMON_FIELDS + ['address', 'animators'] +  LINK_FIELDS)
    w.writeheader()

    for e in queryset.prefetch_related('organizer_configs'):
        d = {k: v for k, v in zip(COMMON_FIELDS, common_extractor(e))}

        d['start_time'] = d['start_time'].astimezone(timezone).strftime('%d/%m %H:%M')
        d['end_time'] = d['end_time'].astimezone(timezone).strftime('%d/%m %H:%M')

        d['description'] = unescape(bleach.clean(d['description'].replace('<br />', '\n'), tags=[], strip=True))

        d['address'] = address_template.format(*address_parts_extractor(e))

        d['animators'] = ' / '.join(
            initiator_template.format(*initiator_extractor(og.person)).strip() for og in e.organizer_configs.all())

        d['link'] = settings.FRONT_DOMAIN + reverse('manage_event', urlconf=front_urls, args=[e.id])
        d['admin_link'] = settings.API_DOMAIN + reverse('admin:events_event_change', args=[e.id])

        w.writerow(d)