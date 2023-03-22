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
