from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.db.models import Exists, Subquery, IntegerField, Func, F
from django.db.models import OuterRef, Count, Q
from django.utils import timezone

from agir.events.models import Event
from agir.groups.models import Membership, SupportGroup, SupportGroupSubtype
from agir.lib.geo import FRENCH_COUNTRY_CODES
from agir.lib.models import (
    Condition,
)

CERTIFICATION_CRITERIA_LABELS = {
    "gender": {
        "label": "Animation paritaire",
        "help": "Le groupe est animé par au moins deux personnes de genre différent",
    },
    "activity": {
        "label": "Trois actions de terrain",
        "help": "Le groupe a organisé trois actions de terrain dans les deux derniers mois",
    },
    "creation": {
        "label": "Un mois d’existence",
        "help": "Le groupe a été créé il y plus d'un mois",
    },
    "members": {
        "label": "Trois membres actifs",
        "help": "Le groupe doit compter plus de trois membres actifs, animateur·ices et gestionnaires compris",
    },
    "exclusivity": {
        "label": "Un seul groupe certifié par animateur·ice",
        "help": "Les animateur·ices du groupe n'animent pas d'autres groupes locaux certifiés",
    },
}


def add_certification_criteria_to_queryset(qs):
    now = timezone.now()

    return (
        qs.annotate(cc_creation=Condition(created__lte=now - timedelta(days=31)))
        .annotate(
            active_member_count=Count(
                "memberships",
                filter=Q(
                    memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MEMBER,
                    memberships__supportgroup__published=True,
                    memberships__person__role__is_active=True,
                ),
                distinct=True,
            )
        )
        .annotate(cc_members=Condition(active_member_count__gte=3))
        .annotate(
            recent_event_count=Count(
                "organized_events",
                filter=Q(
                    organized_events__visibility=Event.VISIBILITY_PUBLIC,
                    organized_events__subtype__is_acceptable_for_group_certification=True,
                    organized_events__start_time__range=(
                        now - timedelta(days=62),
                        now,
                    ),
                ),
                distinct=True,
            )
        )
        .annotate(
            cc_activity=Condition(
                ~Q(location_country__in=FRENCH_COUNTRY_CODES)
                | Q(recent_event_count__gte=3)
            )
        )
        .annotate(
            referent_gender_count=Count(
                "memberships__person__gender",
                filter=Q(
                    memberships__membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
                    memberships__person__role__is_active=True,
                ),
                distinct=True,
            )
        )
        .annotate(cc_gender=Condition(referent_gender_count__gte=2))
        .annotate(
            active_subtypes=Subquery(
                SupportGroupSubtype.objects.active()
                .filter(
                    supportgroups__id=OuterRef("id"),
                )
                .values_list("id", flat=True),
                output_field=ArrayField(base_field=IntegerField()),
            )
        )
        .annotate(active_subtype_ids=F("active_subtypes"))
        .annotate(
            non_exclusive_referents=Exists(
                Membership.objects.filter(
                    membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
                    supportgroup_id=OuterRef("id"),
                )
                .annotate(active_subtype_ids=OuterRef("active_subtype_ids"))
                .annotate(
                    referent_is_referent_of_another_group=Exists(
                        Membership.objects.filter(
                            person_id=OuterRef("person_id"),
                            supportgroup__published=True,
                            membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
                            supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
                            supportgroup__subtypes__in=OuterRef("active_subtype_ids"),
                            supportgroup__certification_date__isnull=False,
                        ).exclude(supportgroup_id=OuterRef("supportgroup_id")),
                    )
                )
                .filter(referent_is_referent_of_another_group=True),
            )
        )
        .annotate(cc_exclusivity=Condition(non_exclusive_referents=False))
        .annotate(
            certifiable=Condition(
                cc_creation=True,
                cc_members=True,
                cc_activity=True,
                cc_gender=True,
                cc_exclusivity=True,
            )
        )
    )


def check_criterium_creation(group):
    # Exists since at least 31 days
    now = timezone.now()
    return now - timedelta(days=31) >= group.created


def check_criterium_members(group):
    # At least 3 active members
    return 3 <= group.active_members_count


def check_criterium_activity(group):
    # At least 3 recent events, except for groups abroad
    if (
        group.location_country
        and group.location_country.code not in FRENCH_COUNTRY_CODES
    ):
        return True

    now = timezone.now()
    recent_event_count = group.organized_events.acceptable_for_group_certification(
        time_ref=now
    ).count()
    return 3 <= recent_event_count


def check_criterium_gender(group):
    from agir.groups.models import Membership

    # At least two referents with different gender
    referents = group.memberships.filter(
        membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT
    )
    referent_genders = (
        referents.exclude(person__gender__exact="")
        .values("person__gender")
        .annotate(c=Count("person__gender"))
        .order_by("person__gender")
        .count()
    )
    return 2 <= referent_genders


def check_criterium_exclusivity(group):
    # Group referents cannot be referents of another certified local group of the same subtype
    exclusivity = True
    for referent in group.referents:
        if not exclusivity:
            break
        exclusivity = (
            False
            == referent.memberships.exclude(supportgroup_id=group.id)
            .filter(
                supportgroup__published=True,
                membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
                supportgroup__type=SupportGroup.TYPE_LOCAL_GROUP,
                supportgroup__subtypes__in=group.subtypes.active(),
                supportgroup__certification_date__isnull=False,
            )
            .exists()
        )

    return exclusivity


def check_certification_criteria(group, with_labels=False):
    criteria = {}

    if hasattr(group, "cc_creation"):
        criteria["creation"] = group.cc_creation
    else:
        criteria["creation"] = check_criterium_creation(group)

    if hasattr(group, "cc_members"):
        criteria["members"] = group.cc_members
    else:
        criteria["members"] = check_criterium_members(group)

    if hasattr(group, "cc_activity"):
        criteria["activity"] = group.cc_activity
    else:
        criteria["activity"] = check_criterium_activity(group)

    if hasattr(group, "cc_gender"):
        criteria["gender"] = group.cc_gender
    else:
        criteria["gender"] = check_criterium_gender(group)

    if hasattr(group, "cc_exclusivity"):
        criteria["exclusivity"] = group.cc_exclusivity
    else:
        criteria["exclusivity"] = check_criterium_exclusivity(group)

    if not with_labels:
        return criteria

    return {
        key: {**labels, "value": criteria.get(key)}
        for key, labels in CERTIFICATION_CRITERIA_LABELS.items()
        if key in criteria.keys()
    }


def check_single_group_and_queryset_criterium_match(qs):
    qs = add_certification_criteria_to_queryset(qs)
    for group in qs:
        print(".", end="")
        print(group.id)
        print(group.subtypes.all())
        if group.cc_creation != check_criterium_creation(group):
            print("creation")
            print(group.id)
        if group.cc_members != check_criterium_members(group):
            print("members")
            print(group.id)
        if group.cc_activity != check_criterium_activity(group):
            print("activity")
            print(group.id)
        if group.cc_gender != check_criterium_gender(group):
            print("gender")
            print(group.id)
        if group.cc_exclusivity != check_criterium_exclusivity(group):
            print("exclusivity")
            print(group.id)
