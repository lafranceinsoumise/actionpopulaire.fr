from django.core import mail
from django.shortcuts import reverse as dj_reverse
from django.test import TestCase
from django.utils import timezone

from agir.people.models import Person
from .. import tasks
from ..models import SupportGroup, Membership


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

    def test_changed_group_notification_mail(self):
        tasks.send_support_group_changed_notification(
            self.group.pk, ["information", "contact"]
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
            # self.assert_(
            #     dj_reverse('quit_group', kwargs={'pk': self.group.pk}, urlconf='front.urls') in message.body,
            #     'quit group link not in message'
            # )
            self.assertIn(
                "/groupes/{}".format(self.group.pk), text, "group link not in message"
            )

            self.assertIn(str(tasks.CHANGE_DESCRIPTION["information"]), text)
            self.assertIn(str(tasks.CHANGE_DESCRIPTION["contact"]), text)
            self.assertNotIn(str(tasks.CHANGE_DESCRIPTION["location"]), text)
