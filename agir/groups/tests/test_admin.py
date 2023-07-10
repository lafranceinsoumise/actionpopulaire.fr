from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from agir.groups.models import SupportGroup, TransferOperation
from agir.people.models import Person


class TransferOperationAdmin(TestCase):
    def setUp(self) -> None:
        self.super_user = Person.objects.create_superperson("super@user.fr", "prout")
        self.client.force_login(
            self.super_user.role, "agir.people.backend.PersonBackend"
        )

        self.people = [
            Person.objects.create_person(
                email=f"{i:02d}@exemple.fr", is_political_support=True
            )
            for i in range(20)
        ]
        self.groups = [
            SupportGroup.objects.create(name="Groupe {i:02d}") for i in range(5)
        ]

        transfers = [(1, 2, [0, 5, 10, 18]), (4, 3, [2, 5, 19])]

        self.transfer_operations = [
            TransferOperation.objects.create(
                former_group=self.groups[i],
                new_group=self.groups[j],
            )
            for i, j, _ in transfers
        ]

        for t, (_, _, k) in zip(self.transfer_operations, transfers):
            t.members.set([self.people[i] for i in k])

    def test_showing_transfer_operation_list(self):
        res = self.client.get(reverse("admin:groups_transferoperation_changelist"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_can_display_transfer_operation(self):
        res = self.client.get(
            reverse(
                "admin:groups_transferoperation_change",
                args=(self.transfer_operations[0].id,),
            )
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
