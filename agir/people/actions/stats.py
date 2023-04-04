import statistics
from datetime import timedelta

from django.utils import timezone
from push_notifications.models import GCMDevice, APNSDevice

from agir.groups.models import Membership, SupportGroup
from agir.lib.data import code_postal_vers_code_departement, departements_par_code
from agir.payments.models import Payment
from agir.people.models import Person
from agir.presidentielle2022.apps import Presidentielle2022Config


def get_statistics_for_queryset(original_queryset):
    person_pks = original_queryset.values_list("pk", flat=True)
    stats = {
        "total": len(person_pks),
        "is_2022": 0,
        "is_insoumise": 0,
        "contacts": 0,
        "known_phone_numbers": 0,
        "newsletter_subscribers": 0,
        "sms_subscribers": 0,
        "last_week_connections": 0,
        "ages": [],
        "genders": {},
        "zip_codes": {},
        "departements": {},
        "groups": 0,
        "group_members": set(),
        "group_referents": set(),
        "certified_group_members": set(),
        "person_groups": set(),
    }

    if stats["total"] == 0:
        return stats

    current_year = timezone.now().year
    one_week_ago = (timezone.now() - timedelta(days=7)).date()
    queryset = Person.objects.filter(pk__in=person_pks).select_related("role")
    genders = {}
    unknown_genders = 0
    user_ids = []

    for person in queryset:
        if person.is_2022:
            stats["is_2022"] += 1
        if person.is_insoumise:
            stats["is_insoumise"] += 1
        if person.date_of_birth:
            stats["ages"].append(current_year - person.date_of_birth.year)
        if person.contact_phone:
            stats["known_phone_numbers"] += 1
        if len(person.newsletters) > 0:
            stats["newsletter_subscribers"] += 1
        if person.subscribed_sms:
            stats["sms_subscribers"] += 1

        if not person.gender:
            unknown_genders += 1
        elif person.gender in genders:
            genders[person.gender] += 1
        else:
            genders[person.gender] = 1

        if (
            person.meta
            and "subscriptions" in person.meta
            and "AP" in person.meta["subscriptions"]
            and "subscriber" in person.meta["subscriptions"]["AP"]
        ):
            stats["contacts"] += 1
        if person.role:
            user_ids.append(person.role_id)
        if (
            person.role
            and person.role.last_login
            and person.role.last_login.date() >= one_week_ago
        ):
            stats["last_week_connections"] += 1

        if person.location_zip:
            if person.location_zip not in stats["zip_codes"]:
                stats["zip_codes"][person.location_zip] = 0
            stats["zip_codes"][person.location_zip] += 1
            code_departement = code_postal_vers_code_departement(person.location_zip)
            if code_departement:
                departement = departements_par_code[code_departement]
                departement = f'{departement.get("id")} - {departement.get("nom")}'
                if departement not in stats["departements"]:
                    stats["departements"][departement] = 0
                stats["departements"][departement] += 1

    stats["liaisons"] = queryset.liaisons().count()

    stats["genders"] = [
        (label, genders.get(key, 0)) for (key, label) in Person.GENDER_CHOICES
    ]
    stats["genders"].append(("Non renseigné", unknown_genders))

    stats["groups"] = SupportGroup.objects.active().count()

    memberships = Membership.objects.filter(
        person_id__in=person_pks,
        membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER,
        supportgroup__published=True,
    ).select_related("supportgroup")

    for membership in memberships:
        stats["person_groups"].add(membership.supportgroup_id)
        stats["group_members"].add(membership.person_id)
        if membership.membership_type >= Membership.MEMBERSHIP_TYPE_REFERENT:
            stats["group_referents"].add(membership.person_id)

    stats["group_members"] = len(stats["group_members"])
    stats["group_referents"] = len(stats["group_referents"])
    stats["person_groups"] = len(stats["person_groups"])
    stats["certified_group_members"] = (
        memberships.filter(supportgroup__certification_date__isnull=False)
        .values("person_id")
        .distinct()
        .count()
    )

    donors = (
        Payment.objects.filter(
            person_id__in=person_pks,
        )
        .values("person_id")
        .distinct()
    )
    stats["is_2022_donors"] = donors.filter(
        type__in=[
            Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
        ],
    ).count()
    stats["is_insoumise_donors"] = donors.exclude(
        type__in=[
            Presidentielle2022Config.DONATION_PAYMENT_TYPE,
            Presidentielle2022Config.DONATION_SUBSCRIPTION_TYPE,
        ],
    ).count()

    if len(stats["ages"]) > 0:
        stats["mean_age"] = statistics.mean(stats["ages"])
        stats["median_age"] = statistics.median(stats["ages"])
        stats["age_pyramid"] = (
            [("0-19", len([age for age in stats["ages"] if age < 20]))]
            + [
                (
                    f"{key}-{key + 9}",
                    len([age for age in stats["ages"] if key <= age <= key + 9]),
                )
                for key in range(20, 90, 10)
            ]
            + [("90+", len([age for age in stats["ages"] if age >= 90]))]
        )

    stats["android_users"] = (
        GCMDevice.objects.filter(active=True, user_id__in=user_ids)
        .values("user_id")
        .distinct()
        .count()
    )
    stats["ios_users"] = (
        APNSDevice.objects.filter(active=True, user_id__in=user_ids)
        .values("user_id")
        .distinct()
        .count()
    )

    return stats
