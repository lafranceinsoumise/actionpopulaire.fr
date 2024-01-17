import csv
import hashlib
from html import unescape
from operator import attrgetter

import bleach
from django.conf import settings
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from weasyprint import HTML

from agir.groups.models import Membership
from agir.lib.export import dicts_to_csv_lines

__all__ = ["groups_to_csv", "groups_to_csv_lines"]


COMMON_FIELDS = [
    "name",
    "published",
    "contact_email",
    "contact_phone",
    "description",
    "location_zip",
    "location_city",
]
ADDRESS_FIELDS = ["location_name", "location_address1", "location_address2"]
LINK_FIELDS = ["link", "admin_link"]

FIELDS = COMMON_FIELDS + ["address", "referents"] + LINK_FIELDS

REFERENT_SIMPLE_FIELDS = ["email", "last_name", "first_name", "contact_phone"]
REFERENT_FIELDS = REFERENT_SIMPLE_FIELDS + [
    "group_name",
    "admin_link",
    "group_link",
    "group_admin_link",
]

common_extractor = attrgetter(*COMMON_FIELDS)
address_parts_extractor = attrgetter(*ADDRESS_FIELDS)

referent_extractor = attrgetter(*REFERENT_SIMPLE_FIELDS)

initiator_template = "{first_name} {last_name} {contact_phone} <{email}>"


def memberships_to_csv(queryset, output):
    w = csv.DictWriter(output, fieldnames=REFERENT_FIELDS)
    w.writeheader()
    w.writerows(memberships_to_dict(queryset))


def groups_to_csv(queryset, output):
    w = csv.DictWriter(output, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(groups_to_dicts(queryset))


def groups_to_csv_lines(queryset):
    return dicts_to_csv_lines(groups_to_dicts(queryset), fieldnames=FIELDS)


def groups_to_dicts(queryset):
    for g in queryset.iterator():
        d = {k: v for k, v in zip(COMMON_FIELDS, common_extractor(g))}
        d["address"] = "\n".join(
            component for component in address_parts_extractor(g) if component
        )
        d["description"] = unescape(
            bleach.clean(d["description"].replace("<br />", "\n"), tags=[], strip=True)
        )

        referents = (
            initiator_template.format(
                **dict(zip(REFERENT_SIMPLE_FIELDS, referent_extractor(m.person)))
            )
            for m in g.memberships.filter(
                membership_type=Membership.MEMBERSHIP_TYPE_REFERENT
            )
        )

        d["referents"] = " / ".join(referents)

        d["link"] = settings.FRONT_DOMAIN + reverse(
            "manage_group", urlconf="agir.api.front_urls", args=[g.id]
        )
        d["admin_link"] = settings.API_DOMAIN + reverse(
            "admin:groups_supportgroup_change",
            urlconf="agir.api.admin_urls",
            args=[g.id],
        )

        yield d


def memberships_to_dict(queryset):
    from agir.api import front_urls

    for m in queryset:
        d = {k: v for k, v in zip(REFERENT_SIMPLE_FIELDS, referent_extractor(m.person))}
        d["group_name"] = m.supportgroup.name
        d["admin_link"] = settings.API_DOMAIN + reverse(
            "admin:people_person_change", args=[m.person_id]
        )
        d["group_link"] = settings.FRONT_DOMAIN + reverse(
            "manage_group", urlconf=front_urls, args=[m.supportgroup_id]
        )
        d["group_admin_link"] = settings.API_DOMAIN + reverse(
            "admin:groups_supportgroup_change", args=[m.supportgroup_id]
        )

        yield d


def group_attendance_list_hash(content):
    dhash = hashlib.md5()
    encoded = content.encode()
    dhash.update(encoded)
    return dhash.hexdigest()


def group_attendance_list_data(group):
    memberships = (
        group.memberships.active()
        .active_members()
        .select_related("person")
        .order_by(
            "-membership_type",
            "person__last_name",
            "person__first_name",
            "person__display_name",
        )
    )
    data = []
    for membership in memberships:
        m = {
            "display_name": membership.person.display_name,
            "last_name": "",
            "first_name": "",
            "description": membership.get_membership_type_display()
            if membership.is_referent
            else "Membre du groupe",
        }
        if membership.personal_information_sharing_consent:
            m.update(
                {
                    "last_name": membership.person.last_name.upper(),
                    "first_name": membership.person.first_name.title(),
                }
            )
        if group.has_automatic_memberships:
            m.update(
                {
                    "description": membership.description,
                    "group": membership.meta.get("group_name", ""),
                }
            )
        data.append(m)

    return data


def pdf_group_attendance_list(group):
    data = group_attendance_list_data(group)
    context = {
        "datetime": timezone.now(),
        "group": group,
        "data": data,
    }
    template = get_template("groups/attendance_list.html")
    html = template.render(context)
    pdf = HTML(string=html).write_pdf()

    return pdf, group_attendance_list_hash(html)
