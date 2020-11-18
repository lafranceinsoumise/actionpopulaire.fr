from unittest import mock

from django.db import IntegrityError
from django.test import TestCase
from rest_framework.test import APITestCase

from agir.groups.tasks import send_someone_joined_notification
from agir.lib.tests.mixins import FakeDataMixin
from agir.people.models import Person
from ..models import SupportGroup, Membership, SupportGroupSubtype


class BasicSupportGroupTestCase(TestCase):
    def test_can_create_supportgroup(self):
        group = SupportGroup.objects.create(name="Groupe d'action")


class MembershipTestCase(APITestCase):
    def setUp(self):
        self.supportgroup = SupportGroup.objects.create(name="Test")

        self.person = Person.objects.create_insoumise(email="marc.machin@truc.com")

        self.privileged_user = Person.objects.create_superperson("super@user.fr", None)

    def test_can_create_membership(self):
        Membership.objects.create(supportgroup=self.supportgroup, person=self.person)

    def test_cannot_create_without_person(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(supportgroup=self.supportgroup)

    def test_cannot_create_without_supportgroup(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(person=self.person)

    def test_unique_membership_for_person_and_group(self):
        Membership.objects.create(person=self.person, supportgroup=self.supportgroup)

        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person, supportgroup=self.supportgroup
            )


class GroupSubtypesTestCase(FakeDataMixin, TestCase):
    def test_local_groups_have_subtype(self):
        self.data["groups"]["user1_group"].subtypes.add(
            SupportGroupSubtype.objects.get(label="groupe local")
        )
