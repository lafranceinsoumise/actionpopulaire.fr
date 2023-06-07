from django.test import TestCase

from agir.groups.forms import TransferGroupMembersForm
from agir.groups.models import SupportGroup, Membership, TransferOperation
from agir.people.models import Person


class TransferFormTestCase(TestCase):
    def test_can_transfer_people(self):
        group1 = SupportGroup.objects.create(name="Groupe 1")
        group2 = SupportGroup.objects.create(name="Groupe 2")

        people = [
            Person.objects.create_person(
                email=f"{i}@domain.fr", is_political_support=True
            )
            for i in range(20)
        ]

        memberships = [
            Membership.objects.create(
                person=p,
                supportgroup=group1,
                membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
            )
            for p in people
        ]

        form = TransferGroupMembersForm(
            manager=people[3],
            former_group=group1,
            data={
                "target_group": group2.id,
                "members": [m.id for m in memberships[15:]],
            },
        )
        form.is_valid()

        self.assertTrue(form.is_valid())

        form.save()

        self.assertCountEqual(group1.members.all(), people[:15])
        self.assertCountEqual(group2.members.all(), people[15:])

        transfer_operation = TransferOperation.objects.first()
        self.assertIsNotNone(transfer_operation)

        self.assertEqual(transfer_operation.manager, people[3])
        self.assertEqual(transfer_operation.former_group, group1)
        self.assertEqual(transfer_operation.new_group, group2)

        self.assertCountEqual(transfer_operation.members.all(), people[15:])
