from faker import Faker
from unittest.mock import patch

from django.db.models import Q
from django.core import mail
from django.db.models import Q
from django.shortcuts import reverse as dj_reverse
from django.test import TestCase
from django.utils import timezone

from agir.lib.tests.mixins import create_group, create_location
from agir.events.models import Event, OrganizerConfig
from agir.people.models import Person
from agir.notifications.models import Subscription
from ...activity.models import Activity
from .. import tasks
from ..actions.notifications import someone_joined_notification
from ..actions.transfer import create_transfer_membership_activities
from ..models import SupportGroup, Membership
from ..tasks import send_joined_notification_email


fake = Faker("fr_FR")


def mock_geocode_element_no_position(supportgroup):
    supportgroup.coordinates = None
    supportgroup.coordinates_type = SupportGroup.COORDINATES_NO_POSITION


def mock_geocode_element_with_position(event):
    location = create_location()
    event.coordinates = location["coordinates"]
    event.coordinates_type = location["coordinates_type"]


class NotificationTasksTestCase(TestCase):
    def setUp(self):
        now = timezone.now()

        self.creator = Person.objects.create_insoumise("moi@moi.fr", create_role=True)
        self.group = SupportGroup.objects.create(
            name="Mon événement",
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
        )

        self.creator_membership = Membership.objects.create(
            person=self.creator,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

        self.member1 = Person.objects.create_insoumise(
            "person1@participants.fr", create_role=True
        )
        self.member2 = Person.objects.create_insoumise(
            "person2@participants.fr", create_role=True
        )
        self.member_no_notification = Person.objects.create_insoumise(
            "person3@participants.fr", create_role=True
        )

        self.membership1 = Membership.objects.create(
            supportgroup=self.group,
            person=self.member1,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.membership2 = Membership.objects.create(
            supportgroup=self.group,
            person=self.member2,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.membership_no_notification = Membership.objects.create(
            supportgroup=self.group,
            person=self.member_no_notification,
            notifications_enabled=False,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        self.group_notification_recipients = [
            self.creator_membership,
            self.membership1,
            self.membership2,
        ]

        Subscription.objects.bulk_create(
            [
                Subscription(
                    person=m.person,
                    membership=m,
                    type=Subscription.SUBSCRIPTION_EMAIL,
                    activity_type=t,
                )
                for m in self.group_notification_recipients
                for t in Subscription.DEFAULT_GROUP_EMAIL_TYPES
            ],
            ignore_conflicts=True,
        )
        Subscription.objects.bulk_create(
            [
                Subscription(
                    person=m.person,
                    membership=m,
                    type=Subscription.SUBSCRIPTION_PUSH,
                    activity_type=t,
                )
                for m in self.group_notification_recipients
                for t in Subscription.DEFAULT_GROUP_PUSH_TYPES
            ],
            ignore_conflicts=True,
        )

        for s in Subscription.objects.filter(person=self.member_no_notification):
            s.delete()

    def test_group_creation_mail(self):
        tasks.send_support_group_creation_notification(self.creator_membership.pk)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.recipients(), ["moi@moi.fr"])

        text = message.body.replace("\n", "")

        self.assertIn(self.group.name, text)

    def test_create_group_creation_confirmation_activity(self):
        original_target_activity_count = Activity.objects.filter(
            type=Activity.TYPE_GROUP_CREATION_CONFIRMATION,
            recipient=self.creator_membership.person,
            supportgroup=self.creator_membership.supportgroup,
        ).count()

        tasks.create_group_creation_confirmation_activity(self.creator_membership.pk)

        new_target_activity_count = Activity.objects.filter(
            type=Activity.TYPE_GROUP_CREATION_CONFIRMATION,
            recipient=self.creator_membership.person,
            supportgroup=self.creator_membership.supportgroup,
        ).count()

        self.assertEqual(new_target_activity_count, original_target_activity_count + 1)

    def test_someone_joined_notification_mail(self):
        send_joined_notification_email(self.membership1.pk)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.recipients(), ["moi@moi.fr"])

        text = message.body.replace("\n", "")

        mail_content = {
            "member information": str(self.member1),
            "group name": self.group.name,
            "group management link": dj_reverse(
                "manage_group",
                kwargs={"pk": self.group.pk},
                urlconf="agir.api.front_urls",
            ),
        }

        for name, value in mail_content.items():
            self.assertTrue(value in text, "{} missing from mail".format(name))

    def test_someone_joined_membership_limit_activity(self):
        supportgroup = SupportGroup.objects.create(
            name="Mon événement",
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
            type=SupportGroup.TYPE_LOCAL_GROUP,
        )

        creator_membership = Membership.objects.create(
            person=self.creator,
            supportgroup=supportgroup,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

        steps = tasks.GROUP_MEMBERSHIP_LIMIT_NOTIFICATION_STEPS

        old_target_activity_count = Activity.objects.filter(
            type=Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
            recipient=creator_membership.person,
            supportgroup=supportgroup,
        ).count()

        for i in range(2, SupportGroup.MEMBERSHIP_LIMIT + 1):
            should_have_activity = (i - SupportGroup.MEMBERSHIP_LIMIT) in steps
            member = Person.objects.create_insoumise("person%d@membe.rs" % i)
            membership = Membership.objects.create(
                supportgroup=supportgroup,
                person=member,
                membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
            )
            someone_joined_notification(membership, membership_count=i)
            new_target_activity_count = Activity.objects.filter(
                type=Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
                recipient=creator_membership.person,
                supportgroup=supportgroup,
            ).count()
            if should_have_activity:
                self.assertEqual(
                    old_target_activity_count + 1,
                    new_target_activity_count,
                    "should create a '%s' activity at %d members"
                    % (Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER, i),
                )
                old_target_activity_count = new_target_activity_count
            else:
                self.assertEqual(
                    old_target_activity_count,
                    new_target_activity_count,
                    "should not create a '%s' activity at %d members"
                    % (Activity.TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER, i),
                )

    def test_changed_group_notification_mail(self):
        tasks.send_support_group_changed_notification(
            self.group.pk, ["name", "contact_name"]
        )

        self.assertEqual(len(mail.outbox), 3)

        for message in mail.outbox:
            self.assertEqual(len(message.recipients()), 1)

        messages = {message.recipients()[0]: message for message in mail.outbox}

        self.assertCountEqual(
            messages.keys(),
            [self.creator.email, self.member1.email, self.member2.email],
        )

        for recipient, message in messages.items():
            text = message.body.replace("\n", "")

            self.assertTrue(self.group.name in text, "group name not in message")
            self.assertIn(
                "/groupes/{}".format(self.group.pk), text, "group link not in message"
            )

    def test_changed_group_activity(self):
        tasks.send_support_group_changed_notification(
            self.group.pk, ["name", "contact_name", "description"]
        )

        activities = Activity.objects.all()
        self.assertEqual(
            activities.count(), 4
        )  # inclut la personne qui a désactivé les notifications
        self.assertCountEqual(
            [a.recipient for a in activities],
            [self.creator, self.member1, self.member2, self.member_no_notification],
        )
        for a in activities:
            self.assertCountEqual(
                a.meta["changed_data"], ["name", "contact_name", "description"]
            )

    def test_send_membership_transfer_notifications_to_transferred_members(self):
        original_group = SupportGroup.objects.create(
            name="Mon événement",
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
        )
        target_group = SupportGroup.objects.create(
            name="Mon événement",
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
        )
        target_group_manager = Membership.objects.create(
            person=self.creator,
            supportgroup=target_group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        transferred_member = Membership.objects.create(
            person=self.member1,
            supportgroup=target_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        old_activity_count = Activity.objects.filter(
            type=Activity.TYPE_TRANSFERRED_GROUP_MEMBER,
            recipient=transferred_member.person,
            supportgroup=target_group,
        ).count()
        create_transfer_membership_activities(
            original_group.pk, target_group.pk, [transferred_member.person.pk]
        )
        new_activity_count = Activity.objects.filter(
            type=Activity.TYPE_TRANSFERRED_GROUP_MEMBER,
            recipient=transferred_member.person,
            supportgroup=target_group,
        ).count()
        self.assertEqual(old_activity_count + 1, new_activity_count)

    def test_send_membership_transfer_notifications_to_target_group_managers(self):
        original_group = SupportGroup.objects.create(
            name="Mon événement",
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
        )
        target_group = SupportGroup.objects.create(
            name="Mon événement",
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
        )
        target_group_manager = Membership.objects.create(
            person=self.creator,
            supportgroup=target_group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        transferred_member = Membership.objects.create(
            person=self.member1,
            supportgroup=target_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        old_activity_count = Activity.objects.filter(
            type=Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
            recipient=transferred_member.person,
            supportgroup=target_group,
        ).count()
        create_transfer_membership_activities(
            original_group.pk, target_group.pk, [transferred_member.person.pk]
        )
        new_activity_count = Activity.objects.filter(
            type=Activity.TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
            recipient=target_group_manager.person,
            supportgroup=target_group,
        ).count()
        self.assertEqual(old_activity_count + 1, new_activity_count)

    @patch("agir.groups.tasks.geocode_element")
    def test_geocode_support_group_calls_geocode_element_if_group_exists(
        self, geocode_element
    ):
        geocode_element.assert_not_called()
        tasks.geocode_support_group(self.group.pk)
        geocode_element.assert_called_once_with(self.group)

    @patch(
        "agir.groups.tasks.geocode_element",
        side_effect=mock_geocode_element_no_position,
    )
    def test_geocode_support_group_creates_activity_if_no_geolocation_is_found(
        self, geocode_element
    ):
        supportgroup = self.group
        managers_filter = (
            Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
        ) & Q(notifications_enabled=True)
        managing_membership = supportgroup.memberships.filter(managers_filter)
        managing_membership_recipients = [
            membership.person for membership in managing_membership
        ]
        old_activity_count = Activity.objects.filter(
            type=Activity.TYPE_WAITING_LOCATION_GROUP,
            recipient__in=managing_membership_recipients,
            supportgroup=supportgroup,
        ).count()
        tasks.geocode_support_group(supportgroup.pk)
        geocode_element.assert_called_once_with(supportgroup)
        supportgroup.refresh_from_db()
        self.assertEqual(
            supportgroup.coordinates_type, SupportGroup.COORDINATES_NO_POSITION
        )

        new_activity_count = Activity.objects.filter(
            type=Activity.TYPE_WAITING_LOCATION_GROUP,
            recipient__in=managing_membership_recipients,
            supportgroup=supportgroup,
        ).count()

        self.assertEqual(
            new_activity_count, old_activity_count + managing_membership.count()
        )

    @patch(
        "agir.groups.tasks.geocode_element",
        side_effect=mock_geocode_element_with_position,
    )
    def test_geocode_support_group_does_not_create_activity_if_geolocation_is_found(
        self, geocode_element
    ):
        supportgroup = self.group
        managers_filter = (
            Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
        ) & Q(notifications_enabled=True)
        managing_membership = supportgroup.memberships.filter(managers_filter)
        managing_membership_recipients = [
            membership.person for membership in managing_membership
        ]
        old_activity_count = Activity.objects.filter(
            type=Activity.TYPE_WAITING_LOCATION_GROUP,
            recipient__in=managing_membership_recipients,
            supportgroup=supportgroup,
        ).count()
        tasks.geocode_support_group(supportgroup.pk)
        geocode_element.assert_called_once_with(supportgroup)
        supportgroup.refresh_from_db()
        self.assertLess(
            supportgroup.coordinates_type, SupportGroup.COORDINATES_NO_POSITION
        )

        new_activity_count = Activity.objects.filter(
            type=Activity.TYPE_WAITING_LOCATION_GROUP,
            recipient__in=managing_membership_recipients,
            supportgroup=supportgroup,
        ).count()

        self.assertEqual(new_activity_count, old_activity_count)

    def test_create_accepted_invitation_member_activity(self):
        supportgroup = self.group

        new_member = Person.objects.create_insoumise("invited@group.member")
        new_membership = Membership.objects.create(
            supportgroup=supportgroup,
            person=new_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        managers_filter = (
            Q(membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER)
        ) & Q(notifications_enabled=True)
        managing_membership = supportgroup.memberships.filter(managers_filter)
        managing_membership_recipients = [
            membership.person for membership in managing_membership
        ]

        old_activity_count = Activity.objects.filter(
            type=Activity.TYPE_ACCEPTED_INVITATION_MEMBER,
            recipient__in=managing_membership_recipients,
            supportgroup=supportgroup,
            individual=new_member,
        ).count()

        tasks.create_accepted_invitation_member_activity(new_membership.pk)

        new_activity_count = Activity.objects.filter(
            type=Activity.TYPE_ACCEPTED_INVITATION_MEMBER,
            recipient__in=managing_membership_recipients,
            supportgroup=supportgroup,
            individual=new_member,
        ).count()

        self.assertEqual(
            new_activity_count, old_activity_count + managing_membership.count()
        )

    def test_new_group_event_notifications_are_sent(self):
        supportgroup = self.group
        recipients = [r.person for r in self.group_notification_recipients]
        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        event = Event.objects.create(
            name="événement test pour groupe",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
            location_name="Lieu de l'événement",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
        )
        OrganizerConfig.objects.create(
            event=event, person=self.creator, as_group=self.group
        )
        old_activity_count = Activity.objects.filter(
            type=Activity.TYPE_NEW_EVENT_MYGROUPS,
            recipient__in=recipients,
            supportgroup=supportgroup,
            event=event,
        ).count()
        tasks.notify_new_group_event(supportgroup.pk, event.pk)
        new_activity_count = Activity.objects.filter(
            type=Activity.TYPE_NEW_EVENT_MYGROUPS,
            recipient__in=recipients,
            supportgroup=supportgroup,
            event=event,
        ).count()
        self.assertEqual(new_activity_count - old_activity_count, len(recipients))

    @patch("agir.groups.tasks.send_mosaico_email")
    def test_new_group_event_emails_are_sent(self, send_mosaico_email):
        supportgroup = self.group
        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        event = Event.objects.create(
            name="événement test pour groupe",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
            location_name="Lieu de l'événement",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
        )
        OrganizerConfig.objects.create(
            event=event, person=self.creator, as_group=self.group
        )
        send_mosaico_email.assert_not_called()
        tasks.send_new_group_event_email(supportgroup.pk, event.pk)
        send_mosaico_email.assert_called_once()
