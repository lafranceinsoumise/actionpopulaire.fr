from datetime import timedelta

from django.conf import settings
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from agir.lib.tests.mixins import FakeDataMixin
from agir.people.models import Person
from ..models import SupportGroup, Membership, SupportGroupSubtype
from ...events.models import Event, OrganizerConfig
from ...msgs.models import SupportGroupMessage


class BasicSupportGroupTestCase(TestCase):
    def test_can_create_supportgroup(self):
        group = SupportGroup.objects.create(name="Groupe d'action")


class SupportGroupCertificationCriteriaTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create("person@agir.test", create_role=True)

    def test_supportgroup_creation(self):
        group = SupportGroup.objects.create(name="G")
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["creation"])
        group.created = timezone.now() - timedelta(days=32)
        group.save()
        group.refresh_from_db()
        criteria = group.check_certification_criteria()
        self.assertTrue(criteria["creation"])

    def test_supportgroup_members(self):
        group = SupportGroup.objects.create(name="G")
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["members"])

        for i in (1, 2, 3):
            person = Person.objects.create_person(f"m{i}@agir.local", create_role=True)
            Membership.objects.create(
                supportgroup=group,
                person=person,
                membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
            )
            criteria = group.check_certification_criteria()
            self.assertEqual(criteria["members"], i == 3)

    def test_supportgroup_activity(self):
        group = SupportGroup.objects.create(name="G", location_country="UK")
        criteria = group.check_certification_criteria()
        self.assertNotIn("activity", criteria)
        group.location_country = "FR"
        group.save()
        group.refresh_from_db()
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["activity"])

        too_old_event = Event.objects.create(
            name="Evenement test",
            visibility=Event.VISIBILITY_PUBLIC,
            start_time=timezone.now() - timedelta(days=93),
            end_time=timezone.now() - timedelta(days=93) + timedelta(minutes=30),
        )
        OrganizerConfig.objects.create(
            event=too_old_event, person=self.person, as_group=group, is_creator=True
        )
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["activity"])

        for i in (1, 2, 3):
            start = timezone.now() - timedelta(days=62) + timedelta(days=i)
            event = Event.objects.create(
                name="Evenement test",
                visibility=Event.VISIBILITY_PUBLIC,
                start_time=start,
                end_time=start + timedelta(minutes=30),
            )
            OrganizerConfig.objects.create(
                event=event, person=self.person, as_group=group, is_creator=True
            )
            criteria = group.check_certification_criteria()
            self.assertEqual(criteria["activity"], i == 3)

    def test_supportgroup_gender(self):
        group = SupportGroup.objects.create(name="G")
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["gender"])

        person = Person.objects.create_person(
            f"f@agir.local", gender=Person.GENDER_FEMALE, create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["gender"])

        person = Person.objects.create_person(
            f"ff@agir.local", gender=Person.GENDER_FEMALE, create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["gender"])

        person = Person.objects.create_person(
            f"m@agir.local", gender=Person.GENDER_MALE, create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["gender"])

        person = Person.objects.create_person(
            f"mm@agir.local", gender=Person.GENDER_MALE, create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = group.check_certification_criteria()
        self.assertTrue(criteria["gender"])

    def test_supportgroup_exclusivity(self):
        group = SupportGroup.objects.create(name="G")
        criteria = group.check_certification_criteria()
        self.assertTrue(criteria["exclusivity"])

        person = Person.objects.create_person(f"f@agir.local", create_role=True)
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = group.check_certification_criteria()
        self.assertTrue(criteria["exclusivity"])

        second_group = SupportGroup.objects.create(name="GG")
        Membership.objects.create(
            supportgroup=second_group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = group.check_certification_criteria()
        self.assertTrue(criteria["exclusivity"])

        subtype = SupportGroupSubtype.objects.create(
            label=settings.CERTIFIED_GROUP_SUBTYPES[0]
        )

        second_group.type = SupportGroup.TYPE_LOCAL_GROUP
        second_group.save()
        criteria = group.check_certification_criteria()
        self.assertTrue(criteria["exclusivity"])

        second_group.subtypes.add(subtype)
        second_group.save()
        second_group.refresh_from_db()
        self.assertTrue(second_group.is_certified)
        criteria = group.check_certification_criteria()
        self.assertFalse(criteria["exclusivity"])


class MembershipTestCase(APITestCase):
    def setUp(self):
        self.supportgroup = SupportGroup.objects.create(name="Test")

        self.person = Person.objects.create_insoumise(email="marc.machin@truc.com")

        self.privileged_user = Person.objects.create_superperson("super@user.fr", None)

    def test_can_create_membership(self):
        Membership.objects.create(
            supportgroup=self.supportgroup,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

    def test_cannot_create_without_person(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                supportgroup=self.supportgroup,
                membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
            )

    def test_cannot_create_without_supportgroup(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
            )

    def test_unique_membership_for_person_and_group(self):
        Membership.objects.create(
            person=self.person,
            supportgroup=self.supportgroup,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person,
                supportgroup=self.supportgroup,
                membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
            )


class GroupSubtypesTestCase(FakeDataMixin, TestCase):
    def test_local_groups_have_subtype(self):
        self.data["groups"]["user1_group"].subtypes.add(
            SupportGroupSubtype.objects.get(label="groupe local")
        )


class MessageTestCase(TestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create()
        self.member = Person.objects.create_person(
            email="member@example.com",
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

    def test_can_create_message(self):
        SupportGroupMessage.objects.create(supportgroup=self.group, author=self.member)
