import csv
from operator import attrgetter
import bleach
from html import unescape


__all__ = ['group_queryset_to_csv']


COMMON_FIELDS = ['name', 'contact_email', 'contact_phone', 'description',]

address_fields = ['location_name', 'location_address1', 'location_zip', 'location_city']

common_extractor = attrgetter(*COMMON_FIELDS)
address_parts_extractor = attrgetter(*address_fields)

initiator_extractor = attrgetter('first_name', 'last_name', 'contact_phone', 'email')

address_template = "{}, {}, {} {}"
initiator_template = "{} {} {} <{}>"


def group_queryset_to_csv(queryset, output):
    w = csv.DictWriter(output, fieldnames=COMMON_FIELDS + ['address', 'animators'])
    w.writeheader()

    for g in queryset.prefetch_related('memberships'):
        d = {k: v for k, v in zip(COMMON_FIELDS, common_extractor(g))}
        d['description'] = unescape(bleach.clean(d['description'].replace('<br />', '\n'), tags=[], strip=True))
        d['address'] = address_template.format(*address_parts_extractor(g))
        d['animators'] = ' / '.join(
            initiator_template.format(*initiator_extractor(m.person)).strip() for m in g.memberships.all() if m.is_referent)
        w.writerow(d)
