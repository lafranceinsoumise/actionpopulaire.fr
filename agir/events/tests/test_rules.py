from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.utils import timezone

from agir.events.models import Event, OrganizerConfig
from agir.groups.models import SupportGroup, Membership
from agir.people.models import Person


class ChangeEventPermissionsTestCase(TestCase):
    def setUp(self) -> None:
        self.event_organizer_group = SupportGroup.objects.create(
            name="Group", published=True
        )
        self.other_group = SupportGroup.objects.create(
            name="Other group", published=True
        )

        self.anonymous = AnonymousUser()

        self.event_creator = Person.objects.create(
            email="event_creator@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.event_organizer_group,
            person=self.event_creator,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.event_organizer = Person.objects.create(
            email="event_organizer@agir.local", create_role=True
        )

        self.event_organizer_group_member = Person.objects.create(
            email="event_organizer_group_member@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.event_organizer_group,
            person=self.event_organizer_group_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        self.event_organizer_group_manager = Person.objects.create(
            email="event_organizer_group_manager@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.event_organizer_group,
            person=self.event_organizer_group_manager,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.event_organizer_group_referent = Person.objects.create(
            email="event_organizer_group_referent@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.event_organizer_group,
            person=self.event_organizer_group_referent,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

        self.other_group_referent = Person.objects.create(
            email="other_group_referent@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.other_group,
            person=self.other_group_referent,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(hours=2)

        self.group_event = Event.objects.create(
            name="Group event", start_time=start_time, end_time=end_time,
        )
        OrganizerConfig.objects.create(
            as_group=self.event_organizer_group,
            person=self.event_creator,
            event=self.group_event,
            is_creator=True,
        )

        OrganizerConfig.objects.create(
            person=self.event_organizer, event=self.group_event, is_creator=False
        )

        self.personal_event = Event.objects.create(
            name="Personal event", start_time=start_time, end_time=end_time,
        )
        OrganizerConfig.objects.create(
            person=self.event_creator, event=self.personal_event
        )

        OrganizerConfig.objects.create(
            person=self.event_organizer, event=self.personal_event, is_creator=False
        )

    def test_anonymous_cannot_change_any_event(self):
        self.assertFalse(
            self.anonymous.has_perm("events.change_event", self.personal_event)
        )
        self.assertFalse(
            self.anonymous.has_perm("events.change_event", self.group_event)
        )

    def test_event_creator_can_change_any_event(self):
        self.assertTrue(
            self.event_creator.has_perm("events.change_event", self.personal_event)
        )
        self.assertTrue(
            self.event_creator.has_perm("events.change_event", self.group_event)
        )

    def test_event_organizer_can_change_any_event(self):
        self.assertTrue(
            self.event_organizer.has_perm("events.change_event", self.personal_event)
        )
        self.assertTrue(
            self.event_organizer.has_perm("events.change_event", self.group_event)
        )

    def test_group_referent_can_change_any_group_organized_event(self):
        self.assertFalse(
            self.event_organizer_group_referent.has_perm(
                "events.change_event", self.personal_event
            )
        )
        self.assertTrue(
            self.event_organizer_group_referent.has_perm(
                "events.change_event", self.group_event
            )
        )
        self.assertFalse(
            self.other_group_referent.has_perm("events.change_event", self.group_event)
        )

    def test_group_manager_cannot_change_any_event(self):
        self.assertFalse(
            self.event_organizer_group_manager.has_perm(
                "events.change_event", self.personal_event
            )
        )
        self.assertFalse(
            self.event_organizer_group_manager.has_perm(
                "events.change_event", self.group_event
            )
        )

    def test_group_member_cannot_change_any_event(self):
        self.assertFalse(
            self.event_organizer_group_member.has_perm(
                "events.change_event", self.personal_event
            )
        )
        self.assertFalse(
            self.event_organizer_group_member.has_perm(
                "events.change_event", self.group_event
            )
        )
