from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.db.models import Q
from django.utils.timezone import now

from agir.events.models import Event
from agir.groups.models import Membership
from agir.lib.admin.utils import admin_url
from agir.lib.utils import front_url

DAYS_SINCE_GROUP_CREATION_LIMIT = 31
DAYS_SINCE_LAST_EVENT_LIMIT = 62


def is_new_group_filter():
    # âge du groupe = maintenant - date de création <= durée max
    # ==>
    # date de création > maintenant - durée max
    limit_group_creation_date = now() - timedelta(days=DAYS_SINCE_GROUP_CREATION_LIMIT)
    return Q(created__gte=limit_group_creation_date)


def has_recent_event_filter():
    # âge de l'événement = maintenant - date événement <= durée max
    # =>
    # date événement >= maintenant - durée max
    limit_event_date = now() - timedelta(days=DAYS_SINCE_LAST_EVENT_LIMIT)
    return Q(
        organized_events__start_time__gte=limit_event_date,
        organized_events__visibility=Event.VISIBILITY_PUBLIC,
    )


def is_active_group_filter():
    return is_new_group_filter() | has_recent_event_filter()


EDITABLE_ONLY_ROUTES = [
    "createSpendingRequest",
    "edit",
    "members",
    "followers",
    "membershipTransfer",
    "geolocate",
    "animation",
    "animationChangeRequest",
    "referentResignmentRequest",
    "deleteGroup",
    "certificationRequest",
]
MEMBER_ONLY_ROUTES = [
    "quit",
    "calendarExport",
]
MANAGER_ONLY_ROUTES = [
    "createEvent",
    "settings",
    "invitation",
    "orders",
    "financement",
    "materiel",
    "createSpendingRequest",
    "edit",
    "members",
    "followers",
    "membershipTransfer",
    "geolocate",
    "downloadMemberList",
]
REFERENT_ONLY_ROUTES = [
    "animation",
    "animationChangeRequest",
    "referentResignmentRequest",
    "deleteGroup",
    "certificationRequest",
]


def get_supportgroup_routes(supportgroup, membership=None, user=None):
    routes = {
        "admin": admin_url("groups_supportgroup_change", args=[supportgroup.pk]),
        "animation": front_url(
            "view_group_settings_management", kwargs={"pk": supportgroup.pk}
        ),
        "animationChangeRequest": "https://actionpopulaire.fr/formulaires/demande-changement-animation-ga/",
        "calendarExport": front_url("ics_group", kwargs={"pk": supportgroup.pk}),
        "createEvent": f'{front_url("create_event")}?group={str(supportgroup.pk)}',
        "createSpendingRequest": front_url(
            "create_group_spending_request", kwargs={"pk": supportgroup.pk}
        ),
        "deleteGroup": "https://actionpopulaire.fr/formulaires/demande-suppression-ga/",
        "details": front_url("view_group", kwargs={"pk": supportgroup.pk}),
        "donations": front_url("supportgroup_donation", kwargs={"pk": supportgroup.pk}),
        "contributions": front_url(
            "supportgroup_contribution", kwargs={"pk": supportgroup.pk}
        ),
        "edit": front_url(
            "view_group_settings_general", kwargs={"pk": supportgroup.pk}
        ),
        "financement": front_url(
            "view_group_settings_finance",
            kwargs={"pk": supportgroup.pk},
        ),
        "followers": front_url(
            "view_group_settings_followers", kwargs={"pk": supportgroup.pk}
        ),
        "geolocate": front_url("change_group_location", kwargs={"pk": supportgroup.pk}),
        "invitation": front_url(
            "view_group_settings_contact",
            kwargs={"pk": supportgroup.pk},
        ),
        "materiel": front_url(
            "view_group_settings_materiel", kwargs={"pk": supportgroup.pk}
        ),
        "members": front_url(
            "view_group_settings_members", kwargs={"pk": supportgroup.pk}
        ),
        "membershipTransfer": front_url(
            "transfer_group_members", kwargs={"pk": supportgroup.pk}
        ),
        "orders": "https://materiel.actionpopulaire.fr/",
        "quit": front_url("quit_group", kwargs={"pk": supportgroup.pk}),
        "referentResignmentRequest": "https://infos.actionpopulaire.fr/contact/",
        "settings": front_url("view_group_settings", kwargs={"pk": supportgroup.pk}),
        "downloadMemberList": front_url(
            "download_member_list", kwargs={"pk": supportgroup.pk}
        ),
    }

    if membership and not supportgroup.is_certified and supportgroup.is_certifiable:
        certification_request_url = (
            "https://lafranceinsoumise.fr/groupes-appui/demande-de-certification/"
        )
        certification_request_params = {
            "group-id": supportgroup.pk,
            "email": membership.person.email,
            "animateur": membership.person.get_full_name(),
        }
        routes[
            "certificationRequest"
        ] = f"{certification_request_url}?{urlencode(certification_request_params)}"

    if not supportgroup.is_certified:
        routes["donations"] = None

    if not supportgroup.tags.filter(label=settings.PROMO_CODE_TAG).exists():
        routes["materiel"] = None

    if not supportgroup.editable:
        for k in EDITABLE_ONLY_ROUTES:
            routes[k] = None

    if not membership:
        for k in set(MEMBER_ONLY_ROUTES + MANAGER_ONLY_ROUTES + REFERENT_ONLY_ROUTES):
            routes[k] = None
    elif membership.membership_type < Membership.MEMBERSHIP_TYPE_MANAGER:
        for k in set(MANAGER_ONLY_ROUTES + REFERENT_ONLY_ROUTES):
            routes[k] = None
    elif membership.membership_type < Membership.MEMBERSHIP_TYPE_REFERENT:
        for k in REFERENT_ONLY_ROUTES:
            routes[k] = None

    if (
        user.is_anonymous
        or not user.person
        or not supportgroup.is_financeable
        or not user.has_perm("groups.view_group_finance", supportgroup)
    ):
        routes["financemement"] = None

    if (
        user.is_anonymous
        or not user.person
        or not user.is_staff
        or not user.has_perm("groups.change_supportgroup")
    ):
        routes["admin"] = None

    return {k: v for k, v in routes.items() if v is not None}
