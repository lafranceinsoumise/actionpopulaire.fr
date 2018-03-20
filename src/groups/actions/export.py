import csv
from operator import attrgetter
import bleach
from html import unescape
from django.conf import settings
from django.urls import reverse

from front import urls as front_urls


__all__ = ['group_queryset_to_csv']


COMMON_FIELDS = ['name', 'contact_email', 'contact_phone', 'description',]
ADDRESS_FIELDS = ['location_name', 'location_address1', 'location_zip', 'location_city']
LINK_FIELDS = ['link', 'admin_link']


common_extractor = attrgetter(*COMMON_FIELDS)
address_parts_extractor = attrgetter(*ADDRESS_FIELDS)

initiator_extractor = attrgetter('first_name', 'last_name', 'contact_phone', 'email')

address_template = "{}, {}, {} {}"
initiator_template = "{} {} {} <{}>"


def group_queryset_to_csv(queryset, output):
    w = csv.DictWriter(output, fieldnames=COMMON_FIELDS + ['address', 'animators'] + LINK_FIELDS)
    w.writeheader()

    for g in queryset.prefetch_related('memberships'):
        d = {k: v for k, v in zip(COMMON_FIELDS, common_extractor(g))}
        d['description'] = unescape(bleach.clean(d['description'].replace('<br />', '\n'), tags=[], strip=True))
        d['address'] = address_template.format(*address_parts_extractor(g))
        d['animators'] = ' / '.join(
            initiator_template.format(*initiator_extractor(m.person)).strip() for m in g.memberships.all() if m.is_referent)

        d['link'] = settings.FRONT_DOMAIN + reverse('manage_group', urlconf=front_urls, args=[g.id])
        d['admin_link'] = settings.API_DOMAIN + reverse('admin:groups_supportgroup_change', args=[g.id])

        w.writerow(d)
