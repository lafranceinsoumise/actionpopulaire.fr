from collections import OrderedDict

from data_france.models import CirconscriptionConsulaire, CirconscriptionLegislative
from django.db.models import F, ExpressionWrapper, BooleanField
from django.db.models import Q

from agir.groups.models import SupportGroup, Membership
from agir.lib.data import departements
from agir.people.models import Person
from agir.people.models import PersonTag

TAG_SUFFIX_FE = "Membre boucle FE {}"
TAG_SUFFIX_DEPARTEMENT = "Membre boucle départementale {}"
QUALIFICATION_PREFIX = "BD__"
FINANCE_QUALIFICATION_LABEL = QUALIFICATION_PREFIX + "finances"


def check_supportgroup_memberships(supportgroup, target_memberships, dry_run=False):
    current_memberships = set(supportgroup.members.values_list("id", flat=True))
    missing_memberships = target_memberships.difference(current_memberships)
    extra_members = current_memberships.difference(target_memberships)

    missing_memberships = [
        Membership(
            supportgroup=supportgroup,
            person_id=p,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        for p in missing_memberships
    ]
    extra_members = Membership.objects.filter(
        supportgroup=supportgroup, person_id__in=extra_members
    )

    if dry_run:
        return current_memberships, len(missing_memberships), len(extra_members)

    _, deleted = extra_members.delete()
    created = Membership.objects.bulk_create(
        missing_memberships, ignore_conflicts=True, send_post_save_signal=True
    )
    current_memberships = list(
        Membership.objects.filter(supportgroup=supportgroup).select_related("person")
    )

    return current_memberships, len(created), deleted.get("groups.Membership", 0)


def apply_changes(supportgroup, target_memberships, metas, dry_run=False):
    updated_memberships, created_count, deleted_count = check_supportgroup_memberships(
        supportgroup, target_memberships, dry_run=dry_run
    )

    if dry_run:
        return len(updated_memberships), created_count, deleted_count

    newsletter_subscribers = []
    for membership in updated_memberships:
        membership.meta = metas[membership.person_id]
        membership.has_finance_managing_privilege = membership.meta.pop(
            "has_finance_managing_privilege", False
        )
        # Ensure members are subscribed to main newsletter choices
        if not membership.person.subscribed:
            membership.person.subscribed = True
            newsletter_subscribers.append(membership.person)

    Membership.objects.bulk_update(
        updated_memberships,
        (
            "has_finance_managing_privilege",
            "meta",
        ),
    )

    if newsletter_subscribers:
        Person.objects.bulk_update(newsletter_subscribers, fields=("newsletters",))

    return (
        len(updated_memberships),
        created_count,
        deleted_count,
    )


def maj_boucle_par_animation(filter):
    groupes_eligibles = (
        SupportGroup.objects.active()
        .certified()
        .filter(type=SupportGroup.TYPE_LOCAL_GROUP)
        .filter(filter)
    )

    ms = (
        Membership.objects.filter(
            supportgroup__in=groupes_eligibles,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        .annotate(supportgroup_name=F("supportgroup__name"))
        .values("person_id", "supportgroup_id", "supportgroup_name")
    )
    membres_souhaites = [m["person_id"] for m in ms]
    metas = {
        m["person_id"]: {
            "description": f"Animateur·ice de groupe d'action",
            "group_id": m["supportgroup_id"],
            "group_name": m["supportgroup_name"],
        }
        for m in ms
    }

    return membres_souhaites, metas


def maj_boucle_par_tag(tag_suffix):
    tags = PersonTag.objects.filter(label__endswith=tag_suffix)

    membres_souhaites = []
    metas = {}

    for tag in tags:
        membres_tags = list(tag.people.values_list("id", flat=True))
        membres_souhaites += membres_tags
        meta = {"tag_id": tag.id, "description": tag.description}
        for person_id in membres_tags:
            metas[person_id] = meta

    return membres_souhaites, metas


def maj_boucle_par_qualification(supportgroup):
    person_qualifications = (
        supportgroup.person_qualifications.select_related("qualification")
        .effective()
        .annotate(
            has_finance_managing_privilege=ExpressionWrapper(
                Q(qualification__label__exact=FINANCE_QUALIFICATION_LABEL),
                output_field=BooleanField(),
            )
        )
        .values(
            "person_id",
            "description",
            "qualification__description",
            "has_finance_managing_privilege",
        )
    )

    metas = {}
    for pq in person_qualifications:
        person_id = pq.pop("person_id")
        q_description = pq.pop("qualification__description")
        description = pq.pop("description") or q_description
        meta = {"description": [description], **pq}

        if person_id in metas:
            meta["description"] = [*metas[person_id]["description"], description]
            meta["has_finance_managing_privilege"] = (
                metas[person_id]["has_finance_managing_privilege"]
                or meta["has_finance_managing_privilege"]
            )

        metas[person_id] = meta

    membres_souhaites = list(metas.keys())

    return membres_souhaites, metas


def maj_boucle_departementale(departement, dry_run=False):
    try:
        boucle_departementale = SupportGroup.objects.get(
            type=SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE,
            location_departement_id=departement.id,
        )
    except SupportGroup.DoesNotExist:
        return None

    membres_animation, metas_animation = maj_boucle_par_animation(departement.filtre)

    membres_tag, metas_tag = maj_boucle_par_tag(
        TAG_SUFFIX_DEPARTEMENT.format(departement.id)
    )

    membres_qualification, metas_qualification = maj_boucle_par_qualification(
        boucle_departementale
    )

    membres = set(membres_animation).union(membres_tag).union(membres_qualification)

    # The order is import here, since the qualification description should override the tag description which should
    # override the default description
    metas = OrderedDict(
        [
            *metas_animation.items(),
            *metas_tag.items(),
            *metas_qualification.items(),
        ]
    )

    return apply_changes(boucle_departementale, membres, metas, dry_run=dry_run)


def maj_boucle_fe(circonscription, dry_run=False):
    numero = int(circonscription.code.split("-")[-1])

    circos_consulaires = CirconscriptionConsulaire.objects.filter(
        circonscription_legislative=circonscription
    ).only("pays")

    pays = set(p for c in circos_consulaires for p in c.pays)

    ordinal = "1ère" if numero == 1 else f"{numero}ème"
    suffixe = f"{ordinal} circonscription des Français de l'étranger"

    try:
        boucle = SupportGroup.objects.get(
            type=SupportGroup.TYPE_BOUCLE_DEPARTEMENTALE,
            name__endswith=suffixe,
        )
    except SupportGroup.DoesNotExist:
        return None

    membres_animation, metas_animation = maj_boucle_par_animation(
        Q(location_country__in=pays)
    )
    membres_tag, metas_tag = maj_boucle_par_tag(
        TAG_SUFFIX_FE.format(circonscription.code)
    )
    membres_qualification, metas_qualification = maj_boucle_par_qualification(boucle)

    membres = set(membres_animation).union(membres_tag).union(membres_qualification)

    # The order is import here, since the qualification description should override the tag description which should
    # override the default description
    metas = OrderedDict(
        [
            *metas_animation.items(),
            *metas_tag.items(),
            *metas_qualification.items(),
        ]
    )

    return apply_changes(boucle, membres, metas, dry_run=dry_run)


def maj_boucles(codes=None, dry_run=False):
    target_departements = departements
    target_circonscriptions = CirconscriptionLegislative.objects.filter(
        code__startswith="99-"
    )

    if codes:
        target_departements = [d for d in target_departements if d.id in codes]
        target_circonscriptions = target_circonscriptions.filter(code__in=codes)

    return {
        **{
            departement: maj_boucle_departementale(
                departement=departement, dry_run=dry_run
            )
            for departement in target_departements
        },
        **{
            circonscription: maj_boucle_fe(
                circonscription=circonscription, dry_run=dry_run
            )
            for circonscription in target_circonscriptions
        },
    }


def update_memberships_from_segment(supportgroup, dry_run=False):
    target_memberships = set(
        supportgroup.membership_segment.get_people().values_list("id", flat=True)
    )
    updated_memberships, created_count, deleted_count = check_supportgroup_memberships(
        supportgroup, target_memberships, dry_run=dry_run
    )
    if dry_run:
        return len(updated_memberships), created_count, deleted_count

    for membership in updated_memberships:
        membership.meta["from_membership_segment"] = supportgroup.membership_segment.pk

    Membership.objects.bulk_update(
        updated_memberships,
        ("meta",),
    )

    return (
        len(updated_memberships),
        created_count,
        deleted_count,
    )


def refresh_supportgroups_with_membership_segment(supportgroups, dry_run=False):
    return {
        supportgroup: update_memberships_from_segment(supportgroup, dry_run=dry_run)
        for supportgroup in supportgroups
    }
