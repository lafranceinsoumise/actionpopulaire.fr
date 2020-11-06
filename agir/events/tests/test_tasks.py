from django.test import TestCase
from django.utils import timezone
from django.core import mail

from agir.lib.utils import front_url
from agir.people.models import Person

from .. import tasks
from ..models import Event, Calendar, RSVP, OrganizerConfig


class EventTasksTestCase(TestCase):
    def setUp(self):
        now = timezone.now()

        self.calendar = Calendar.objects.create_calendar("default")

        self.creator = Person.objects.create_insoumise("moi@moi.fr")
        self.event = Event.objects.create(
            name="Mon événement",
            start_time=now + timezone.timedelta(hours=2),
            end_time=now + timezone.timedelta(hours=3),
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

        self.organizer_config = OrganizerConfig.objects.create(
            person=self.creator, event=self.event
        )

        self.attendee1 = Person.objects.create_insoumise("person1@participants.fr")
        self.attendee2 = Person.objects.create_insoumise("person2@participants.fr")
        self.attendee_no_notification = Person.objects.create_insoumise(
            "person3@participants.fr"
        )

        self.rsvp1 = RSVP.objects.create(event=self.event, person=self.attendee1)
        self.rsvp2 = RSVP.objects.create(event=self.event, person=self.attendee2)
        self.rsvp3 = RSVP.objects.create(
            event=self.event,
            person=self.attendee_no_notification,
            notifications_enabled=False,
        )

    def test_event_creation_mail(self):
        tasks.send_event_creation_notification(self.organizer_config.pk)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.recipients(), ["moi@moi.fr"])

        text = message.body

        for item in [
            "name",
            "location_name",
            "short_address",
            "contact_name",
            "contact_phone",
        ]:
            self.assert_(
                getattr(self.event, item) in text, "{} missing in message".format(item)
            )

    def test_rsvp_notification_mail(self):
        tasks.send_rsvp_notification(self.rsvp1.pk)

        self.assertEqual(len(mail.outbox), 2)

        attendee_message = mail.outbox[0]
        self.assertEqual(attendee_message.recipients(), ["person1@participants.fr"])

        text = attendee_message.body.replace("\n", "")
        mail_content = {
            "event name": self.event.name,
            "event link": front_url("view_event", kwargs={"pk": self.event.pk}),
        }

        for name, value in mail_content.items():
            self.assert_(value in text, "{} missing from mail".format(name))

        org_message = mail.outbox[1]
        self.assertEqual(org_message.recipients(), ["moi@moi.fr"])

        text = org_message.body.replace("\n", "")

        mail_content = {
            "attendee information": str(self.attendee1),
            "event name": self.event.name,
            "event management link": front_url(
                "manage_event", kwargs={"pk": self.event.pk}
            ),
        }

        for name, value in mail_content.items():
            self.assert_(value in text, "{} missing from mail".format(name))

    def test_changed_event_notification_mail(self):
        tasks.send_event_changed_notification(self.event.pk, ["information", "timing"])

        self.assertEqual(len(mail.outbox), 2)

        for message in mail.outbox:
            self.assertEqual(len(message.recipients()), 1)

        messages = {message.recipients()[0]: message for message in mail.outbox}

        self.assertCountEqual(
            messages.keys(), [self.attendee1.email, self.attendee2.email]
        )

        for recipient, message in messages.items():
            text = message.body.replace("\n", "")

            self.assert_(self.event.name in text, "event name not in message")
            self.assert_(
                front_url("quit_event", kwargs={"pk": self.event.pk}) in text,
                "quit event link not in message",
            )

            self.assert_(str(tasks.CHANGE_DESCRIPTION["information"]) in text)
            self.assert_(str(tasks.CHANGE_DESCRIPTION["timing"]) in text)
            self.assert_(str(tasks.CHANGE_DESCRIPTION["contact"]) not in text)

    def test_send_event_report_mail(self):
        tasks.send_event_report(self.event.pk)
        self.assertEqual(len(mail.outbox), 2)

        text = mail.outbox[0].body
        self.assert_(self.event.name in text)
        self.assert_(self.event.report_content[:100] in text)
        tasks.send_event_report(self.event.pk)
        # on verifie qu'il n'y a pas de mail suplémentaire
        self.assertEqual(len(mail.outbox), 2)
