from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import now

# Create your tests here.
from agir.mailing.models import Segment
from agir.people.models import Person


class SegmentTestCase(TestCase):
    def setUp(self) -> None:
        self.person_with_account = Person.objects.create_insoumise(
            email="a@a.a",
            create_role=True,
        )

        self.person_without_account = Person.objects.create_person(email="b@b.b")

    def test_default_segment_include_anyone(self):
        s = Segment.objects.create(newsletters=[], is_insoumise=None)

        self.assertIn(self.person_with_account, s.get_subscribers_queryset())
        self.assertIn(self.person_without_account, s.get_subscribers_queryset())

    def test_person_with_disabled_account_not_in_segment(self):
        s = Segment.objects.create(newsletters=[], is_insoumise=None)
        role = self.person_with_account.role
        role.is_active = False
        role.save()

        self.assertNotIn(self.person_with_account, s.get_subscribers_queryset())

    def test_segment_with_registration_duration(self):
        old_person = Person.objects.create_person(
            email="old@agir.local", created=now() - timedelta(hours=2)
        )
        new_person = Person.objects.create_person(email="new@agir.local", created=now())
        s = Segment.objects.create(
            newsletters=[], is_insoumise=None, registration_duration=1
        )
        self.assertIn(old_person, s.get_subscribers_queryset())
        self.assertNotIn(new_person, s.get_subscribers_queryset())
