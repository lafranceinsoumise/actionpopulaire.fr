from faker import Faker
from unittest.mock import patch

from django.core import mail
from django.shortcuts import reverse as dj_reverse
from django.test import TestCase
from django.utils import timezone

from agir.people.models import Person
from .. import tasks
from ..models import SupportGroup, Membership
from ...activity.models import Activity
from agir.lib.tests.mixins import create_group

fake = Faker("fr_FR")


class NotificationTasksTestCase(TestCase):
    def setUp(self):
        now = timezone.now()

        self.creator = Person.objects.create_insoumise("moi@moi.fr")
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

        self.member1 = Person.objects.create_insoumise("person1@participants.fr")
        self.member2 = Person.objects.create_insoumise("person2@participants.fr")
        self.member_no_notification = Person.objects.create_insoumise(
            "person3@participants.fr"
        )

        self.membership1 = Membership.objects.create(
            supportgroup=self.group, person=self.member1
        )
        self.membership2 = Membership.objects.create(
            supportgroup=self.group, person=self.member2
        )
        self.membership3 = Membership.objects.create(
            supportgroup=self.group,
            person=self.member_no_notification,
            notifications_enabled=False,
        )

    def test_group_creation_mail(self):
        tasks.send_support_group_creation_notification(self.creator_membership.pk)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.recipients(), ["moi@moi.fr"])

        text = message.body.replace("\n", "")

        for item in [
            "name",
            "location_name",
            "short_address",
            "contact_name",
            "contact_phone",
        ]:
            self.assert_(
                getattr(self.group, item) in text, "{} missing in message".format(item)
            )

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
        tasks.send_someone_joined_notification(self.membership1.pk)

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
            self.assert_(value in text, "{} missing from mail".format(name))

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
                supportgroup=supportgroup, person=member
            )
            tasks.send_someone_joined_notification(membership.pk, membership_count=i)
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

            self.assert_(self.group.name in text, "group name not in message")
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
        tasks.send_membership_transfer_notifications(
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
        tasks.send_membership_transfer_notifications(
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

    @patch("agir.groups.tasks.geocode_element")
    def test_geocode_support_group_does_not_call_geocode_element_if_group_does_not_exist(
        self, geocode_element
    ):
        geocode_element.assert_not_called()
        tasks.geocode_support_group(fake.uuid4())
        geocode_element.assert_not_called()
