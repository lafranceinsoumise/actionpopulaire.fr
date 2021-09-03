from faker import Faker
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from django.core import mail

from agir.lib.tests.mixins import create_location
from agir.lib.utils import front_url
from agir.people.models import Person
from agir.notifications.models import Subscription

from .. import tasks
from ..models import Event, Calendar, RSVP, OrganizerConfig
from ...activity.models import Activity
from ...groups.models import SupportGroup, Membership

fake = Faker("fr_FR")


def mock_geocode_element_no_position(event):
    event.coordinates = None
    event.coordinates_type = Event.COORDINATES_NO_POSITION


def mock_geocode_element_with_position(event):
    location = create_location()
    event.coordinates = location["coordinates"]
    event.coordinates_type = location["coordinates_type"]


class EventTasksTestCase(TestCase):
    def setUp(self):
        now = timezone.now()

        self.calendar = Calendar.objects.create_calendar("default")

        self.creator = Person.objects.create_insoumise("moi@moi.fr", create_role=True)
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

        self.event_no_email = Event.objects.create(
            name="Un événement",
            start_time=now + timezone.timedelta(hours=2),
            end_time=now + timezone.timedelta(hours=3),
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place de la Bastille",
            location_zip="75011",
            location_city="Paris",
            location_country="FR",
        )

        self.attendee1 = Person.objects.create_insoumise(
            "person1@participants.fr", create_role=True
        )
        self.attendee2 = Person.objects.create_insoumise(
            "person2@participants.fr", create_role=True
        )
        self.attendee_no_notification = Person.objects.create_insoumise(
            "person3@participants.fr", create_role=True
        )

        self.organizer_group = SupportGroup.objects.create(name="Groupe")
        Membership.objects.create(
            supportgroup=self.organizer_group,
            person=self.creator,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        Membership.objects.create(
            supportgroup=self.organizer_group,
            person=self.attendee1,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        Membership.objects.create(
            supportgroup=self.organizer_group,
            person=self.attendee2,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        Membership.objects.create(
            supportgroup=self.organizer_group,
            person=self.attendee_no_notification,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        self.organizer_config = OrganizerConfig.objects.create(
            person=self.creator, event=self.event, as_group=self.organizer_group
        )

        self.organizer_config2 = OrganizerConfig.objects.create(
            person=self.attendee_no_notification, event=self.event
        )

        self.rsvp1 = RSVP.objects.create(event=self.event, person=self.attendee1)
        self.rsvp2 = RSVP.objects.create(event=self.event, person=self.attendee2)
        self.rsvp3 = RSVP.objects.create(
            event=self.event,
            person=self.attendee_no_notification,
            notifications_enabled=False,
        )

        Subscription.objects.filter(person=self.attendee_no_notification).delete()

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
        tasks.send_event_changed_notification(self.event.pk, ["name", "start_time"])

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

    def test_changed_event_notification_mail_no_subscriptions(self):
        tasks.send_event_changed_notification(
            self.event_no_email.pk, ["name", "start_time"]
        )

        self.assertEqual(len(mail.outbox), 0)

    def test_changed_event_activity(self):
        tasks.send_event_changed_notification(
            self.event.pk, ["name", "start_time", "end_time"]
        )

        self.assertEqual(len(mail.outbox), 2)

    def test_send_event_report_mail(self):
        tasks.send_event_report(self.event.pk)
        self.assertEqual(len(mail.outbox), 2)

        text = mail.outbox[0].body
        self.assert_(self.event.name in text)
        self.assert_(self.event.report_content[:100] in text)
        tasks.send_event_report(self.event.pk)
        # on verifie qu'il n'y a pas de mail suplémentaire
        self.assertEqual(len(mail.outbox), 2)

    @patch("agir.events.tasks.geocode_element")
    def test_geocode_event_calls_geocode_element_if_event_exists(self, geocode_element):
        geocode_element.assert_not_called()
        tasks.geocode_event(self.event.pk)
        geocode_element.assert_called_once_with(self.event)

    @patch(
        "agir.events.tasks.geocode_element",
        side_effect=mock_geocode_element_no_position,
    )
    def test_geocode_event_creates_activity_if_no_geolocation_is_found(
        self, geocode_element
    ):
        event = self.event
        organizers = event.organizers.all()
        old_activity_count = Activity.objects.filter(
            type=Activity.TYPE_WAITING_LOCATION_EVENT,
            recipient__in=organizers,
            event=event,
        ).count()
        tasks.geocode_event(event.pk)
        geocode_element.assert_called_once_with(event)
        event.refresh_from_db()
        self.assertEqual(event.coordinates_type, Event.COORDINATES_NO_POSITION)

        new_activity_count = Activity.objects.filter(
            type=Activity.TYPE_WAITING_LOCATION_EVENT,
            recipient__in=organizers,
            event=event,
        ).count()

        self.assertEqual(new_activity_count, old_activity_count + organizers.count())

    @patch(
        "agir.events.tasks.geocode_element",
        side_effect=mock_geocode_element_with_position,
    )
    def test_geocode_event_does_not_create_activity_if_geolocation_is_found(
        self, geocode_element
    ):
        event = self.event
        organizers = event.organizers.all()
        old_activity_count = Activity.objects.filter(
            type=Activity.TYPE_WAITING_LOCATION_EVENT,
            recipient__in=organizers,
            event=event,
        ).count()
        tasks.geocode_event(event.pk)
        geocode_element.assert_called_once_with(event)
        event.refresh_from_db()
        self.assertLess(event.coordinates_type, Event.COORDINATES_NO_POSITION)

        new_activity_count = Activity.objects.filter(
            type=Activity.TYPE_WAITING_LOCATION_EVENT,
            recipient__in=organizers,
            event=event,
        ).count()

        self.assertEqual(new_activity_count, old_activity_count)
