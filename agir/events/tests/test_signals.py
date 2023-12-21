from django.test import TestCase
from django.utils import timezone
from faker import Faker

from agir.groups.models import SupportGroup, Membership
from agir.people.models import Person
from ..models import Event

fake = Faker("fr_FR")


class SignalTransferGroupOrganizerConfigToGroupReferentsTestCase(TestCase):
    def create_person(self):
        return Person.objects.create_insoumise(fake.email())

    def create_group(self, referents=None, managers=None):
        group = SupportGroup.objects.create(
            name="Un groupe",
        )
        referents = referents or []
        for referent in referents:
            group.memberships.create(
                person=referent, membership_type=Membership.MEMBERSHIP_TYPE_REFERENT
            )

        managers = managers or []
        for manager in managers:
            group.memberships.create(
                person=manager, membership_type=Membership.MEMBERSHIP_TYPE_MANAGER
            )

        return group

    def create_event(self, creator=None, as_group=None, extra_organizers=None):
        now = timezone.now()
        event = Event.objects.create_event(
            organizer_person=creator,
            organizer_group=as_group,
            name="Mon événement",
            start_time=now + timezone.timedelta(hours=2),
            end_time=now + timezone.timedelta(hours=3),
        )

        return event

    def add_event_organizer(self, event, organizer, as_group=None):
        event.organizer_configs.create(person=organizer, as_group=as_group)

    def test_organizer_config_is_transferred_to_group_referents_upon_person_deletion(
        self,
    ):
        group_referents = [self.create_person(), self.create_person()]
        group_managers = [
            self.create_person(),
            self.create_person(),
            self.create_person(),
        ]
        leaving_person = self.create_person()
        group = self.create_group(referents=group_referents, managers=group_managers)
        group_event = self.create_event(creator=leaving_person, as_group=group)
        self.assertIn(leaving_person, group_event.organizers.all())
        leaving_person.delete()
        self.assertNotIn(leaving_person, group_event.organizers.all())
        self.assertIn(group, group_event.organizers_groups.all())
        self.assertEqual(group_event.organizer_configs.count(), len(group_referents))

    def test_organizer_config_is_transferred_to_group_managers_upon_person_deletion_if_group_has_no_referents(
        self,
    ):
        group_managers = [
            self.create_person(),
            self.create_person(),
            self.create_person(),
        ]
        leaving_person = self.create_person()
        group = self.create_group(referents=None, managers=group_managers)
        group_event = self.create_event(creator=leaving_person, as_group=group)
        self.assertIn(leaving_person, group_event.organizers.all())
        leaving_person.delete()
        self.assertNotIn(leaving_person, group_event.organizers.all())
        self.assertIn(group, group_event.organizers_groups.all())
        self.assertEqual(group_event.organizer_configs.count(), len(group_managers))

    def test_organizer_config_is_transferred_to_group_referents_upon_people_deletion(
        self,
    ):
        group_referents = [self.create_person(), self.create_person()]
        leaving_people = [self.create_person(), self.create_person()]
        group = self.create_group(referents=group_referents)
        group_event = self.create_event(creator=leaving_people[0], as_group=group)
        self.add_event_organizer(group_event, organizer=leaving_people[1])
        self.assertIn(leaving_people[0], group_event.organizers.all())
        self.assertIn(leaving_people[1], group_event.organizers.all())
        Person.objects.filter(id__in=[p.id for p in leaving_people]).delete()
        self.assertNotIn(leaving_people[0], group_event.organizers.all())
        self.assertNotIn(leaving_people[1], group_event.organizers.all())
        self.assertIn(group, group_event.organizers_groups.all())
        self.assertEqual(group_event.organizer_configs.count(), 2)

    def test_organizer_config_is_transferred_to_group_referents_upon_person_deletion_even_if_configs_exist_for_another_group(
        self,
    ):
        leaving_person = self.create_person()
        group_referents = [self.create_person(), self.create_person()]
        another_group_organizer = self.create_person()
        group = self.create_group(referents=group_referents)
        another_group = self.create_group(referents=[another_group_organizer])
        group_event = self.create_event(creator=leaving_person, as_group=group)
        self.add_event_organizer(
            group_event, another_group_organizer, as_group=another_group
        )
        self.assertIn(leaving_person, group_event.organizers.all())
        leaving_person.delete()
        self.assertNotIn(leaving_person, group_event.organizers.all())
        self.assertIn(group, group_event.organizers_groups.all())
        self.assertEqual(group_event.organizer_configs.count(), 3)

    def test_organizer_config_is_not_transferred_for_personal_events_upon_person_deletion(
        self,
    ):
        leaving_person = self.create_person()
        personal_event = self.create_event(creator=leaving_person, as_group=None)
        self.assertIn(leaving_person, personal_event.organizers.all())
        leaving_person.delete()
        self.assertFalse(personal_event.organizer_configs.exists())

    def test_organizer_config_is_not_transferred_to_group_referents_upon_person_deletion_if_another_exist_for_the_group(
        self,
    ):
        group_referents = [self.create_person(), self.create_person()]
        leaving_person = self.create_person()
        group = self.create_group(referents=group_referents)
        group_event = self.create_event(creator=leaving_person, as_group=group)
        self.add_event_organizer(group_event, group_referents[0], as_group=group)
        self.assertIn(leaving_person, group_event.organizers.all())
        leaving_person.delete()
        self.assertNotIn(leaving_person, group_event.organizers.all())
        self.assertIn(group, group_event.organizers_groups.all())
        self.assertEqual(group_event.organizer_configs.count(), 1)

    def test_organizer_config_is_not_transferred_to_group_referents_upon_person_deletion_if_the_group_has_no_manager(
        self,
    ):
        leaving_person = self.create_person()
        group = self.create_group(referents=None, managers=None)
        group_event = self.create_event(creator=leaving_person, as_group=group)
        self.assertIn(leaving_person, group_event.organizers.all())
        leaving_person.delete()
        self.assertNotIn(leaving_person, group_event.organizers.all())
        self.assertNotIn(group, group_event.organizers_groups.all())
        self.assertFalse(group_event.organizer_configs.exists())
