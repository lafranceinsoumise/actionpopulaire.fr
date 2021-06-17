from agir.groups.models import Membership
from agir.notifications.models import Subscription


def get_default_person_subscriptions(person):
    subscriptions = []

    for activity_type in Subscription.DEFAULT_PERSON_EMAIL_TYPES:
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

    for activity_type in Subscription.DEFAULT_GROUP_EMAIL_TYPES:
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
