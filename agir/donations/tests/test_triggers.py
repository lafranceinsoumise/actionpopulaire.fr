from django.db import IntegrityError, transaction
from django.test import TestCase

from agir.donations.models import Operation, Spending, MonthlyAllocation
from agir.groups.models import SupportGroup
from agir.payments.models import Payment, Subscription
from agir.people.models import Person


class TriggersTestCaseMixin:
    def setUp(self):
        self.group1 = SupportGroup.objects.create(
            name="Groupe 1", type=SupportGroup.TYPE_LOCAL_GROUP
        )

        self.group2 = SupportGroup.objects.create(
            name="Groupe 2", type=SupportGroup.TYPE_LOCAL_GROUP
        )

        self.group3 = SupportGroup.objects.create(
            name="Groupe 3", type=SupportGroup.TYPE_LOCAL_GROUP
        )

    def create_payment(self, amount, group=None, allocation=None):
        """Crée un paiement, et optionnellement une opération"""
        p = Payment.objects.create(
            status=Payment.STATUS_COMPLETED, price=amount, type="don", mode="system_pay"
        )

        if group is not None:
            Operation.objects.create(
                payment=p, amount=allocation or p.price, group=group
            )

        return p

    def create_subscription(self, amount, person, group=None, allocation=None):
        s = Subscription.objects.create(person=person, price=amount)

        if group is not None:
            MonthlyAllocation.objects.create(
                amount=allocation, subscription=s, group=group
            )


class AllocationTestCase(TriggersTestCaseMixin, TestCase):
    def test_can_allocate_less_than_payment(self):
        self.create_payment(1000, group=self.group1)
        self.create_payment(1000, group=self.group2, allocation=500)

    def test_cannot_allocate_more_than_payment(self):
        p = self.create_payment(1000)
        with self.assertRaises(IntegrityError):
            Operation.objects.create(payment=p, group=self.group1, amount=1500)

    def test_cannot_allocate_more_than_payment_in_several_operations(self):
        p = self.create_payment(1000, group=self.group1, allocation=800)
        with self.assertRaises(IntegrityError):
            Operation.objects.create(payment=p, group=self.group2, amount=500)

    def test_cannot_reduce_payment_if_allocated(self):
        p = self.create_payment(1000, group=self.group1, allocation=600)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                p.price = 500
                p.save()

        Operation.objects.create(payment=p, group=self.group2, amount=200)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                p.price = 700
                p.save()

    def test_spending_cannot_reference_payment(self):
        p = self.create_payment(1000)

        with self.assertRaises(IntegrityError):
            Operation.objects.create(amount=-200, payment=p, group=self.group1)

    def test_can_create_positive_operation_without_payment(self):
        Operation.objects.create(amount=500, group=self.group1)


class SpendingTestCase(TriggersTestCaseMixin, TestCase):
    def test_can_spend_less_than_allocation(self):
        self.create_payment(1000, group=self.group1, allocation=500)
        Spending.objects.create(group=self.group1, amount=-300)

    def test_can_spend_less_than_multiple_allocations(self):
        self.create_payment(1000, group=self.group1, allocation=800)
        self.create_payment(1000, group=self.group1, allocation=800)
        Spending.objects.create(group=self.group1, amount=-1500)

    def test_cannot_spend_more_than_allocation(self):
        self.create_payment(1000, group=self.group1)
        with self.assertRaises(IntegrityError):
            Spending.objects.create(group=self.group1, amount=-1800)

    def test_cannot_spend_allocation_from_other_group(self):
        self.create_payment(1000, group=self.group1)
        with self.assertRaises(IntegrityError):
            Spending.objects.create(group=self.group2, amount=-800)

    def test_cannot_reallocation_operation_if_it_creates_integrity_error(self):
        self.create_payment(1000, group=self.group1)
        o = Operation.objects.get()
        s = Spending.objects.create(group=self.group1, amount=-800)
        with self.assertRaises(IntegrityError):
            o.group = self.group2
            o.save()

    def test_cannot_spend_more_in_several_times(self):
        self.create_payment(1000, group=self.group1, allocation=600)
        self.create_payment(1000, group=self.group1, allocation=600)

        Spending.objects.create(group=self.group1, amount=-500)
        Spending.objects.create(group=self.group1, amount=-500)
        with self.assertRaises(IntegrityError):
            Spending.objects.create(group=self.group1, amount=-500)

    def test_cannot_spend_more_by_modifying_spending(self):
        self.create_payment(1000, group=self.group1, allocation=500)

        s = Spending.objects.create(group=self.group1, amount=-500)

        s.amount = -600
        with self.assertRaises(IntegrityError):
            s.save()

    def test_cannot_spend_more_by_modifying_allocation(self):
        p = self.create_payment(1000, group=self.group1)
        o = Operation.objects.get(payment=p)

        Spending.objects.create(group=self.group1, amount=-800)

        o.amount = 500
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                o.save()

        with self.assertRaises(IntegrityError):
            o.delete()


class MonthlyAllocationTestCase(TriggersTestCaseMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.p1 = Person.objects.create_person("test@test.com")

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
