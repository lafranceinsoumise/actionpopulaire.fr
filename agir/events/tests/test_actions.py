import uuid

from agir.people.person_forms.models import PersonForm, PersonFormSubmission
from django.test import TestCase
from django.utils import timezone

from agir.groups.models import SupportGroup
from agir.lib.tests.mixins import create_location
from agir.people.models import Person
from ..actions import notifications
from ..actions.notifications import event_report_form_reminder_notification
from ..models import Event, RSVP, OrganizerConfig, EventSubtype
from ...activity.models import Activity


class EventSuggestionNotificationsActionsTestCase(TestCase):
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


class EventReportFormReminderNotificationActionTestCase(TestCase):
    def setUp(self):
        now = timezone.now()
        self.creator = Person.objects.create_insoumise("creator@event.ap")
        self.published_form = PersonForm.objects.create(
            title="ABC",
            short_description="ABCDEF",
            slug="published_form",
            published=True,
        )
        unpublished_form = PersonForm.objects.create(
            title="ABC",
            short_description="ABCDEF",
            slug="unpublished_form",
            published=False,
        )

        subtype_without_form = EventSubtype.objects.create(
            label="ST without form", report_person_form=None
        )
        self.event_without_form = Event.objects.create(
            name="event_without_form",
            start_time=now - timezone.timedelta(hours=2),
            end_time=now - timezone.timedelta(hours=3),
            subtype=subtype_without_form,
        )
        OrganizerConfig.objects.create(
            person=self.creator, event=self.event_without_form, is_creator=True
        )

        subtype_with_unpublished_form = EventSubtype.objects.create(
            label="ST with unpublished form", report_person_form=unpublished_form
        )
        self.event_with_unpublished_form = Event.objects.create(
            name="event_with_unpublished_form",
            start_time=now - timezone.timedelta(hours=2),
            end_time=now - timezone.timedelta(hours=3),
            subtype=subtype_with_unpublished_form,
        )
        OrganizerConfig.objects.create(
            person=self.creator, event=self.event_with_unpublished_form, is_creator=True
        )

        subtype_with_form = EventSubtype.objects.create(
            label="ST with form", report_person_form=self.published_form
        )
        self.event_with_form = Event.objects.create(
            name="event_with_form",
            start_time=now - timezone.timedelta(hours=2),
            end_time=now - timezone.timedelta(hours=3),
            subtype=subtype_with_form,
        )
        OrganizerConfig.objects.create(
            person=self.creator, event=self.event_with_form, is_creator=True
        )

        self.event_with_submitted_form = Event.objects.create(
            name="event_with_submitted_form",
            start_time=now - timezone.timedelta(hours=2),
            end_time=now - timezone.timedelta(hours=3),
            subtype=subtype_with_form,
        )
        OrganizerConfig.objects.create(
            person=self.creator, event=self.event_with_submitted_form, is_creator=True
        )
        PersonFormSubmission.objects.create(
            form=self.published_form,
            person=self.creator,
            data={"reported_event_id": str(self.event_with_submitted_form.pk)},
        )

    def test_reminder_activity_is_not_created_if_event_does_not_exist(self):
        unexisting_event_pk = uuid.uuid4()
        self.assertFalse(Event.objects.filter(id=unexisting_event_pk).exists())
        initial_count = len(
            Activity.objects.filter(
                type=Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
            )
        )
        event_report_form_reminder_notification(unexisting_event_pk)
        final_count = len(
            Activity.objects.filter(
                type=Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
            )
        )
        self.assertEqual(initial_count, final_count)

    def test_reminder_activity_is_not_created_for_event_with_no_form(self):
        self.assertIsNone(self.event_without_form.subtype.report_person_form)
        event_report_form_reminder_notification(self.event_without_form.pk)
        self.assertFalse(
            Activity.objects.filter(
                type=Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
                event=self.event_without_form,
            ).exists()
        )

    def test_reminder_activity_is_not_created_for_event_with_unpublished_form(self):
        self.assertFalse(
            self.event_with_unpublished_form.subtype.report_person_form.published
        )
        event_report_form_reminder_notification(self.event_with_unpublished_form.pk)
        self.assertFalse(
            Activity.objects.filter(
                type=Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
                event=self.event_with_unpublished_form,
            ).exists()
        )

    def test_reminder_activity_is_not_created_for_event_with_submitted_form(self):
        self.assertTrue(
            self.event_with_submitted_form.subtype.report_person_form.submissions.filter(
                data__reported_event_id=self.event_with_submitted_form.pk
            ).exists()
        )
        event_report_form_reminder_notification(self.event_with_submitted_form.pk)
        self.assertFalse(
            Activity.objects.filter(
                type=Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
                event=self.event_with_submitted_form,
            ).exists()
        )

    def test_reminder_activity_is_created_for_event(self):
        event_report_form_reminder_notification(self.event_with_form.pk)
        activity = Activity.objects.filter(
            type=Activity.TYPE_REMINDER_REPORT_FORM_FOR_EVENT,
            event=self.event_with_form,
        ).first()
        self.assertIsNotNone(activity)
        self.assertEqual(activity.meta.get("slug"), self.published_form.slug)
        self.assertEqual(activity.meta.get("title"), self.published_form.title)
        self.assertEqual(
            activity.meta.get("description"), self.published_form.meta_description
        )
