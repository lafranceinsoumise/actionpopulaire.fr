from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from agir.events.models import Event
from agir.groups.models import Membership, SupportGroup, SupportGroupSubtype
from agir.lib.geo import FRENCH_COUNTRY_CODES

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

SQL_QUERY = """
WITH active_people_person AS (
    SELECT
        pp.*
    FROM
        people_person pp
        LEFT JOIN authentication_role ar ON pp.role_id = ar.id
    WHERE
        NOT ar.is_active IS FALSE
),
creation AS (
  SELECT 
    id AS supportgroup_id, 
    created <= %(now)s - INTERVAL '%(creation_limit_days)s days' AS satisfied 
  FROM 
    groups_supportgroup
), 
members AS (
  SELECT 
    gm.supportgroup_id, 
    COUNT(DISTINCT gm.person_id) >= %(member_limit_n)s AS satisfied 
  FROM 
    groups_membership gm 
    INNER JOIN active_people_person pp ON gm.person_id = pp.id AND gm.membership_type >= %(membership_type_member)s
  GROUP BY 
    gm.supportgroup_id
), 
activity AS (
  SELECT 
    eo.as_group_id AS supportgroup_id, 
    COUNT(DISTINCT eo.event_id) >= %(activity_limit_n)s AS satisfied 
  FROM 
    events_organizerconfig eo 
    INNER JOIN events_event ee ON (
        ee.id = eo.event_id 
        AND eo.as_group_id IS NOT NULL 
        AND ee.visibility = %(event_visibility_public)s 
        AND ee.start_time BETWEEN %(now)s - INTERVAL '%(activity_limit_days)s days' AND %(now)s
    ) 
    INNER JOIN events_eventsubtype est ON (
      ee.subtype_id = est.id 
      AND est.is_acceptable_for_group_certification IS TRUE
    )
  GROUP BY 
    eo.as_group_id
), 
activity_abroad AS (
  SELECT 
    id AS supportgroup_id, 
    TRUE AS satisfied 
  FROM 
    groups_supportgroup
  WHERE
    NOT (
        location_country = ''
        OR location_country = ANY(%(french_countries)s)
    )
), 
gender AS (
  SELECT 
    gm.supportgroup_id, 
    COUNT(DISTINCT pp.gender) >= %(gender_limit_n)s AS satisfied 
  FROM 
    groups_membership gm 
    INNER JOIN active_people_person pp ON (
        gm.person_id = pp.id 
        AND NOT pp.gender = ''
        AND gm.membership_type >= %(membership_type_referent)s 
    )
  GROUP BY 
    gm.supportgroup_id
),
non_exclusive_referent_group AS (
  SELECT
    DISTINCT m.supportgroup_id
  FROM groups_membership m
  INNER JOIN active_people_person pp ON m.person_id = pp.id 
  INNER JOIN groups_supportgroup_subtypes gs ON gs.supportgroup_id = m.supportgroup_id
  INNER JOIN groups_membership om ON (
    m.person_id = om.person_id
    AND om.supportgroup_id != m.supportgroup_id 
  )
  INNER JOIN groups_supportgroup og ON (
    og.id = om.supportgroup_id
    AND og.published IS TRUE
    AND og.certification_date IS NOT NULL
  )
  INNER JOIN groups_supportgroup_subtypes ogs ON (
    om.supportgroup_id = ogs.supportgroup_id
    AND ogs.supportgroupsubtype_id = gs.supportgroupsubtype_id
    AND ogs.supportgroupsubtype_id IN (
        SELECT
          supportgroupsubtype_id
        FROM
          groups_supportgroup_subtypes
        WHERE
          supportgroupsubtype_id = ANY(%(supportgroupsubtype_ids)s)
      )
  )
  WHERE
    m.membership_type = %(membership_type_referent)s AND om.membership_type = %(membership_type_referent)s
),
exclusivity AS (
    SELECT
      g.id AS supportgroup_id,
      non_exclusive_referent_group.supportgroup_id IS NULL AS satisfied
    FROM
      groups_supportgroup g
    LEFT JOIN non_exclusive_referent_group ON non_exclusive_referent_group.supportgroup_id = g.id
),
criteria AS (
    SELECT 
      g.id AS supportgroup_id, 
      COALESCE(creation.satisfied, FALSE) AS cc_creation, 
      COALESCE(members.satisfied, FALSE) AS cc_members, 
      CASE
        WHEN COALESCE(activity_abroad.satisfied, FALSE) THEN NULL 
        ELSE COALESCE(activity.satisfied, FALSE) 
        END cc_activity, 
      COALESCE(gender.satisfied, FALSE) AS cc_gender, 
      COALESCE(exclusivity.satisfied, TRUE) AS cc_exclusivity
    FROM 
      groups_supportgroup g 
      LEFT JOIN creation ON creation.supportgroup_id = g.id 
      LEFT JOIN members ON members.supportgroup_id = g.id 
      LEFT JOIN gender ON gender.supportgroup_id = g.id 
      LEFT JOIN activity ON activity.supportgroup_id = g.id
      LEFT JOIN activity_abroad ON activity_abroad.supportgroup_id = g.id
      LEFT JOIN exclusivity ON exclusivity.supportgroup_id = g.id 
) 
SELECT 
  g.id,
  cc_creation, 
  cc_members, 
  cc_activity, 
  cc_gender, 
  cc_exclusivity,
  (
    cc_creation 
    AND cc_members 
    AND cc_gender 
    AND cc_exclusivity 
    AND cc_activity IS NOT FALSE
  ) AS certifiable
FROM 
  groups_supportgroup g 
  LEFT JOIN criteria ON criteria.supportgroup_id = g.id  
WHERE 
  g.id = ANY(%(supportgroup_ids)s)
"""

PARAMS = {
    "french_countries": FRENCH_COUNTRY_CODES,
    "supportgroup_type_local": SupportGroup.TYPE_LOCAL_GROUP,
    "membership_type_member": Membership.MEMBERSHIP_TYPE_MEMBER,
    "membership_type_referent": Membership.MEMBERSHIP_TYPE_REFERENT,
    "event_visibility_public": Event.VISIBILITY_PUBLIC,
    "creation_limit_days": 31,
    "member_limit_n": 3,
    "activity_limit_n": 3,
    "activity_limit_days": 62,
    "gender_limit_n": 2,
}


def get_params(qs=None):
    params = {
        **PARAMS,
        "now": timezone.now(),
        "supportgroupsubtype_ids": list(
            SupportGroupSubtype.objects.active().values_list("id", flat=True)
        ),
    }

    if qs:
        params["supportgroup_ids"] = list(qs.values_list("id", flat=True))

    return params


def certification_criteria_for_queryset(qs):
    params = get_params(qs)

    return SupportGroup.objects.raw(SQL_QUERY, params=params)


def check_criterion_creation(group, params=None):
    if params is None:
        params = get_params()

    now = params.get("now")
    creation_limit_days = params.get("creation_limit_days")

    return now - timedelta(days=creation_limit_days) >= group.created


def check_criterion_members(group, params=None):
    if params is None:
        params = get_params()

    return (
        params.get("member_limit_n")
        <= group.memberships.exclude(
            person__role__isnull=False, person__role__is_active=False
        )
        .filter(membership_type__gte=params.get("membership_type_member"))
        .count()
    )


def check_criterion_activity(group, params=None):
    if params is None:
        params = get_params()

    if group.location_country and group.location_country.code not in params.get(
        "french_countries"
    ):
        return None

    recent_event_count = group.organized_events.acceptable_for_group_certification(
        limit_days=params.get("activity_limit_days"), time_ref=params.get("now")
    ).count()

    return params.get("activity_limit_n") <= recent_event_count


def check_criterion_gender(group, params=None):
    if params is None:
        params = get_params()

    referents = group.memberships.filter(
        membership_type__gte=params.get("membership_type_referent")
    )
    referent_genders = (
        referents.exclude(person__gender__exact="")
        .values("person__gender")
        .annotate(c=Count("person__gender"))
        .order_by("person__gender")
        .count()
    )
    return params.get("gender_limit_n") <= referent_genders


def check_criterion_exclusivity(group, params=None):
    if params is None:
        params = get_params()
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
                membership_type__gte=params.get("membership_type_referent"),
                supportgroup__type=params.get("supportgroup_type_local"),
                supportgroup__subtypes__id__in=group.subtypes.active(),
                supportgroup__certification_date__isnull=False,
            )
            .exists()
        )

    return exclusivity


def check_certification_criteria(group, with_labels=False):
    params = get_params()
    criteria = {}

    if hasattr(group, "cc_creation"):
        criteria["creation"] = group.cc_creation
    else:
        criteria["creation"] = check_criterion_creation(group, params)

    if hasattr(group, "cc_members"):
        criteria["members"] = group.cc_members
    else:
        criteria["members"] = check_criterion_members(group, params)

    if hasattr(group, "cc_activity"):
        criteria["activity"] = group.cc_activity
    else:
        criteria["activity"] = check_criterion_activity(group, params)

    if hasattr(group, "cc_gender"):
        criteria["gender"] = group.cc_gender
    else:
        criteria["gender"] = check_criterion_gender(group, params)

    if hasattr(group, "cc_exclusivity"):
        criteria["exclusivity"] = group.cc_exclusivity
    else:
        criteria["exclusivity"] = check_criterion_exclusivity(group, params)

    if not with_labels:
        return {key: val is not False for key, val in criteria.items()}

    return {
        key: {**labels, "value": criteria.get(key)}
        for key, labels in CERTIFICATION_CRITERIA_LABELS.items()
        if key in criteria.keys() and criteria.get(key) is not None
    }


def check_single_group_and_queryset_criterion_match(qs):
    params = get_params(qs)
    qs = certification_criteria_for_queryset(qs)

    for group in qs:
        print(".", end="")
        if group.cc_creation != check_criterion_creation(group, params):
            print("\ncreation")
            print(group.id)
        if group.cc_members != check_criterion_members(group, params):
            print("\nmembers")
            print(group.id)
        if group.cc_activity != check_criterion_activity(group, params):
            print("\nactivity")
            print(group.id)
        if group.cc_gender != check_criterion_gender(group, params):
            print("\ngender")
            print(group.id)
        if group.cc_exclusivity != check_criterion_exclusivity(group, params):
            print("\nexclusivity")
            print(group.id)

    return qs
