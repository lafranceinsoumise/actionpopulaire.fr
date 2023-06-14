from agir.groups.models import Membership
from agir.notifications.models import Subscription


def get_default_person_email_subscriptions(person):
    return [
        Subscription(
            person=person,
            type=Subscription.SUBSCRIPTION_EMAIL,
            activity_type=activity_type,
        )
        for activity_type in Subscription.DEFAULT_PERSON_EMAIL_TYPES
    ]


def get_default_group_email_subscriptions(person, membership):
    return [
        Subscription(
            person=person,
            type=Subscription.SUBSCRIPTION_EMAIL,
            activity_type=activity_type,
            membership=membership,
        )
        for activity_type in Subscription.DEFAULT_GROUP_EMAIL_TYPES
    ]


def get_default_person_push_subscriptions(person):
    return [
        Subscription(
            person=person,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=activity_type,
        )
        for activity_type in Subscription.DEFAULT_PERSON_PUSH_TYPES
    ]


def get_default_group_push_subscriptions(person, membership):
    return [
        Subscription(
            person=person,
            type=Subscription.SUBSCRIPTION_PUSH,
            activity_type=activity_type,
            membership=membership,
        )
        for activity_type in Subscription.DEFAULT_GROUP_PUSH_TYPES
    ]


def create_default_person_email_subscriptions(person):
    subscriptions = get_default_person_email_subscriptions(person)
    person_memberships = Membership.objects.filter(person=person).distinct()

    if person_memberships.exists():
        for membership in person_memberships:
            subscriptions += get_default_group_email_subscriptions(person, membership)

    Subscription.objects.bulk_create(subscriptions)


def create_default_person_push_subscriptions(person):
    subscriptions = get_default_person_push_subscriptions(person)
    person_memberships = Membership.objects.filter(person=person).distinct()

    if person_memberships.exists():
        for membership in person_memberships:
            subscriptions += get_default_group_push_subscriptions(person, membership)

    Subscription.objects.bulk_create(subscriptions)


def create_default_group_membership_subscriptions(person, membership):
    if not membership.id:
        membership = Membership.objects.get(
            supportgroup=membership.supportgroup, person=membership.person
        )
    subscriptions = get_default_group_push_subscriptions(person, membership)
    subscriptions += get_default_group_email_subscriptions(person, membership)
    Subscription.objects.bulk_create(subscriptions)
