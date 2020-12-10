from django.test import TestCase

# Create your tests here.
from agir.mailing.models import Segment
from agir.people.models import Person


class SegmentTestCase(TestCase):
    def setUp(self) -> None:
        self.person_with_account = Person.objects.create_insoumise(
            email="a@a.a", create_role=True,
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
