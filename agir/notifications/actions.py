from agir.activity.models import Activity
from agir.groups.models import Membership
from agir.notifications.models import Subscription

DEFAULT_PERSON_SUBSCRIPTION_ACTIVITY_TYPES = [
    Activity.TYPE_GROUP_INVITATION,
    Activity.TYPE_WAITING_LOCATION_EVENT,
    Activity.TYPE_NEW_ATTENDEE,
    Activity.TYPE_EVENT_UPDATE,
    Activity.TYPE_CANCELLED_EVENT,
    Activity.TYPE_REFERRAL,
    Activity.TYPE_TRANSFERRED_GROUP_MEMBER,
    Activity.TYPE_WAITING_PAYMENT,
    Activity.TYPE_NEW_EVENT_AROUNDME,
    Activity.TYPE_EVENT_SUGGESTION,
]

DEFAULT_GROUP_SUBSCRIPTION_ACTIVITY_TYPES = [
    Activity.TYPE_GROUP_COORGANIZATION_INFO,
    Activity.TYPE_NEW_MESSAGE,
    Activity.TYPE_NEW_COMMENT,
    Activity.TYPE_GROUP_INFO_UPDATE,
    Activity.TYPE_NEW_EVENT_MYGROUPS,
    Activity.TYPE_NEW_REPORT,
    Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED,
    Activity.TYPE_GROUP_COORGANIZATION_INVITE,
    Activity.TYPE_WAITING_LOCATION_GROUP,
    Activity.TYPE_NEW_MEMBER,
    Activity.TYPE_ACCEPTED_INVITATION_MEMBER,
    Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
    Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
]


def get_default_person_subscriptions(person):
    subscriptions = []

    for activity_type in DEFAULT_PERSON_SUBSCRIPTION_ACTIVITY_TYPES:
        subscriptions += [
            Subscription(
                person=person,
                type=Subscription.SUBSCRIPTION_EMAIL,
                activity_type=activity_type,
            ),
            Subscription(
                person=person,
                type=Subscription.SUBSCRIPTION_PUSH,
                activity_type=activity_type,
            ),
        ]

    return subscriptions


def get_default_group_subscriptions(person, membership):
    subscriptions = []

    for activity_type in DEFAULT_GROUP_SUBSCRIPTION_ACTIVITY_TYPES:
        subscriptions += [
            Subscription(
                person=person,
                type=Subscription.SUBSCRIPTION_EMAIL,
                activity_type=activity_type,
                membership=membership,
            ),
            Subscription(
                person=person,
                type=Subscription.SUBSCRIPTION_PUSH,
                activity_type=activity_type,
                membership=membership,
            ),
        ]

    return subscriptions


def create_default_person_subscriptions(person):
    subscriptions = get_default_person_subscriptions(person)
    person_memberships = Membership.objects.filter(person=person).distinct()

    if person_memberships.exists():
        for membership in person_memberships:
            subscriptions += get_default_group_subscriptions(person, membership)

    Subscription.objects.bulk_create(subscriptions)


def create_default_group_membership_subscriptions(person, membership):
    subscriptions = get_default_group_subscriptions(person, membership)
    Subscription.objects.bulk_create(subscriptions)
