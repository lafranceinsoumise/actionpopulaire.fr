from django.db import IntegrityError, transaction
from django.test import TestCase

from agir.donations.models import MonthlyAllocation
from agir.groups.models import SupportGroup
from agir.payments.models import Subscription
from agir.people.models import Person


class MonthlyAllocationTestCase(TestCase):
    def setUp(self) -> None:
        self.group1 = SupportGroup.objects.create(
            name="Groupe 1", type=SupportGroup.TYPE_LOCAL_GROUP
        )

        self.group2 = SupportGroup.objects.create(
            name="Groupe 2", type=SupportGroup.TYPE_LOCAL_GROUP
        )

        self.group3 = SupportGroup.objects.create(
            name="Groupe 3", type=SupportGroup.TYPE_LOCAL_GROUP
        )
        self.p1 = Person.objects.create_insoumise("test@test.com")

    def create_subscription(self, amount, person, group=None, allocation=None):
        s = Subscription.objects.create(person=person, price=amount)

        if group is not None:
            MonthlyAllocation.objects.create(
                amount=allocation, subscription=s, group=group
            )

    def test_cannot_create_single_allocation_bigger_than_subscription(self):
        s = self.create_subscription(1000, self.p1)
        with self.assertRaises(IntegrityError):
            MonthlyAllocation.objects.create(
                amount=1400, subscription=s, group=self.group1
            )

    def test_cannot_create_multiple_allocations_bigger_than_subscription(self):
        s = self.create_subscription(1000, self.p1, allocation=500, group=self.group1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MonthlyAllocation.objects.create(
                    amount=1000, subscription=s, group=self.group2
                )

        MonthlyAllocation(amount=400, subscription=s, group=self.group2)

        with self.assertRaises(IntegrityError):
            MonthlyAllocation.objects.create(
                amount=200, subscription=s, group=self.group3
            )

    def test_can_create_multiple_allocations(self):
        s = self.create_subscription(1000, self.p1)

        MonthlyAllocation(amount=400, subscription=s, group=self.group1)
        MonthlyAllocation(amount=400, subscription=s, group=self.group2)
        MonthlyAllocation(amount=200, subscription=s, group=self.group3)

    def test_cannot_create_two_allocations_with_same_group(self):
        s = self.create_subscription(1000, self.p1, group=self.group1, allocation=400)

        with self.assertRaises(IntegrityError):
            MonthlyAllocation.objects.create(
                subscription=s, amount=300, group=self.group1
            )
