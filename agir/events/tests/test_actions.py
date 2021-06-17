from django.test import TestCase
from django.utils import timezone
from django.core import mail

from agir.lib.utils import front_url
from agir.lib.tests.mixins import create_location
from agir.groups.models import SupportGroup
from agir.people.models import Person

from ..actions import notifications
from ..models import Event, Calendar, RSVP, OrganizerConfig
from ...activity.models import Activity


class EventNotificationsActionsTestCase(TestCase):
    def setUp(self):
        now = timezone.now()
        location = create_location()

        self.creator = Person.objects.create_insoumise("creator@event.ap")
        self.event = Event.objects.create(
            name="Mon événement",
            start_time=now + timezone.timedelta(hours=2),
            end_time=now + timezone.timedelta(hours=3),
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            **location,
        )

        self.person_organizer_config = OrganizerConfig.objects.create(
            person=self.creator, event=self.event, is_creator=True
        )

        self.group = SupportGroup.objects.create(
            name="Mon groupe",
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            **location,
        )
        self.group_event = Event.objects.create(
            name="Mon événement",
            start_time=now + timezone.timedelta(hours=2),
            end_time=now + timezone.timedelta(hours=3),
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            **location,
        )

        self.group_organizer_config = OrganizerConfig.objects.create(
            person=self.creator, event=self.group_event, as_group=self.group
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

    def test_new_event_suggestion_with_person_organized_event(self):
        original_target_activity_count = Activity.objects.filter(
            type=Activity.TYPE_EVENT_SUGGESTION,
            recipient=self.attendee1,
            individual=self.event.organizers.first(),
        ).count()

        notifications.new_event_suggestion_notification(self.event, self.attendee1)

        new_target_activity_count = Activity.objects.filter(
            type=Activity.TYPE_EVENT_SUGGESTION,
            recipient=self.attendee1,
            individual=self.event.organizers.first(),
        ).count()

        self.assertEqual(new_target_activity_count, original_target_activity_count + 1)

    def test_new_event_suggestion_with_group_organized_event(self):
        original_target_activity_count = Activity.objects.filter(
            type=Activity.TYPE_EVENT_SUGGESTION,
            recipient=self.attendee1,
            supportgroup=self.group_event.organizers_groups.first(),
        ).count()
        notifications.new_event_suggestion_notification(
            self.group_event, self.attendee1
        )

        new_target_activity_count = Activity.objects.filter(
            type=Activity.TYPE_EVENT_SUGGESTION,
            recipient=self.attendee1,
            supportgroup=self.group_event.organizers_groups.first(),
        ).count()

        self.assertEqual(new_target_activity_count, original_target_activity_count + 1)
