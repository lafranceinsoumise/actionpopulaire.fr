from agir.activity.models import Activity
from agir.groups.models import Membership
from agir.notifications.models import Subscription

DEFAULT_PERSON_SUBSCRIPTION_ACTIVITY_TYPES = [
    # GENERAL
    Activity.TYPE_TRANSFERRED_GROUP_MEMBER,
    Activity.TYPE_GROUP_INVITATION,
    # mandatory :
    # Activity.TYPE_WAITING_PAYMENT,
    # EVENTS
    Activity.TYPE_EVENT_SUGGESTION,
    Activity.TYPE_EVENT_UPDATE,
    # NEW REPORT not for groups only ? (from excel)
    Activity.TYPE_NEW_ATTENDEE,
    Activity.TYPE_WAITING_LOCATION_EVENT,
    # mandatory :
    # Activity.TYPE_CANCELLED_EVENT,
    # No mail sent :
    # Activity.TYPE_REFERRAL,
]

DEFAULT_GROUP_SUBSCRIPTION_ACTIVITY_TYPES = [
    Activity.TYPE_NEW_EVENT_MYGROUPS,
    Activity.TYPE_GROUP_COORGANIZATION_INFO,
    Activity.TYPE_GROUP_INFO_UPDATE,
    Activity.TYPE_NEW_MESSAGE,
    Activity.TYPE_NEW_COMMENT,
    Activity.TYPE_NEW_REPORT,
    Activity.TYPE_NEW_MEMBER,
    Activity.TYPE_ACCEPTED_INVITATION_MEMBER,
    # mandatory
    # Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
    Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
    Activity.TYPE_WAITING_LOCATION_GROUP,
    Activity.TYPE_GROUP_COORGANIZATION_INVITE,
    Activity.TYPE_GROUP_CREATION_CONFIRMATION,
    Activity.TYPE_GROUP_COORGANIZATION_ACCEPTED,
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
