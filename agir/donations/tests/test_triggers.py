from django.db import IntegrityError, transaction
from django.test import TestCase

from agir.donations.models import Operation, Spending
from agir.groups.models import SupportGroup
from agir.payments.models import Payment


class FinancialTriggersTestCase(TestCase):
    def setUp(self):
        self.group1 = SupportGroup.objects.create(
            name="Groupe 1", type=SupportGroup.TYPE_LOCAL_GROUP
        )

        self.group2 = SupportGroup.objects.create(
            name="Groupe 2", type=SupportGroup.TYPE_LOCAL_GROUP
        )

    def create_payment(self, amount, group=None, allocation=None):
        p = Payment.objects.create(
            status=Payment.STATUS_COMPLETED, price=amount, type="don", mode="system_pay"
        )

        if group is not None:
            Operation.objects.create(
                payment=p, amount=allocation or p.price, group=group
            )

        return p

    def test_can_allocate_less_than_payment(self):
        self.create_payment(1000, group=self.group1)
        self.create_payment(1000, group=self.group2, allocation=500)

    def test_cannot_allocate_more_than_payment(self):
        p = self.create_payment(1000)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Operation.objects.create(payment=p, group=self.group1, amount=1500)

        Operation.objects.create(payment=p, group=self.group1, amount=800)
        with self.assertRaises(IntegrityError):
            Operation.objects.create(payment=p, group=self.group2, amount=500)

    def test_cannot_reduce_payment_if_allocated(self):
        p = self.create_payment(1000, group=self.group1, allocation=900)
        with self.assertRaises(IntegrityError):
            p.price = 800
            p.save()

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
