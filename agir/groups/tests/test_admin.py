from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from agir.groups import admin
from agir.groups.admin.filters import LastManagerLoginFilter
from agir.groups.models import SupportGroup, TransferOperation, Membership
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


class LastManagerLoginFilterTest(TestCase):
    def setUp(self) -> None:
        today = timezone.now()

        self.recently_logged_in_group = SupportGroup.objects.create(
            name="recently_logged_in"
        )
        self.recently_logged_in_person = Person.objects.create_person(
            "today@agir.test", create_role=True
        )
        self.recently_logged_in_person.role.last_login = today
        self.recently_logged_in_person.role.save()
        Membership.objects.create(
            person=self.recently_logged_in_person,
            supportgroup=self.recently_logged_in_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.one_month_old_login_group = SupportGroup.objects.create(
            name="one_month_old_login"
        )
        self.one_month_old_login_person = Person.objects.create_person(
            "one_month@agir.test", create_role=True
        )
        self.one_month_old_login_person.role.last_login = today - relativedelta(
            months=1, days=5
        )
        self.one_month_old_login_person.role.save()
        Membership.objects.create(
            person=self.one_month_old_login_person,
            supportgroup=self.one_month_old_login_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.two_month_old_login_group = SupportGroup.objects.create(
            name="two_month_old_login"
        )
        self.two_month_old_login_person = Person.objects.create_person(
            "two_month@agir.test", create_role=True
        )
        self.two_month_old_login_person.role.last_login = today - relativedelta(
            months=2, days=5
        )
        self.two_month_old_login_person.role.save()
        Membership.objects.create(
            person=self.two_month_old_login_person,
            supportgroup=self.two_month_old_login_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.not_yet_logged_in_group = SupportGroup.objects.create(
            name="not_yet_logged_in"
        )
        self.not_yet_logged_in_person = Person.objects.create_person(
            "never@agir.test", create_role=False
        )
        Membership.objects.create(
            person=self.not_yet_logged_in_person,
            supportgroup=self.not_yet_logged_in_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

    def test_test_data_is_ok(self):
        self.assertEqual(
            self.recently_logged_in_person.role.last_login,
            self.recently_logged_in_group.get_last_manager_login(),
        )
        self.assertEqual(
            self.one_month_old_login_person.role.last_login,
            self.one_month_old_login_group.get_last_manager_login(),
        )
        self.assertEqual(
            self.two_month_old_login_person.role.last_login,
            self.two_month_old_login_group.get_last_manager_login(),
        )
        self.assertIsNone(self.not_yet_logged_in_group.get_last_manager_login())

    def test_empty_filter(self):
        f = LastManagerLoginFilter(
            None,
            {"last_manager_login": None},
            SupportGroup,
            admin.SupportGroupAdmin,
        )
        filtered_qs = f.queryset(None, SupportGroup.objects.all())
        self.assertIn(self.recently_logged_in_group, filtered_qs)
        self.assertIn(self.one_month_old_login_group, filtered_qs)
        self.assertIn(self.two_month_old_login_group, filtered_qs)
        self.assertIn(self.not_yet_logged_in_group, filtered_qs)

    def test_invalid_filter(self):
        f = LastManagerLoginFilter(
            None,
            {"last_manager_login": "2_months_from_now"},
            SupportGroup,
            admin.SupportGroupAdmin,
        )
        filtered_qs = f.queryset(None, SupportGroup.objects.all())
        self.assertIn(self.recently_logged_in_group, filtered_qs)
        self.assertIn(self.one_month_old_login_group, filtered_qs)
        self.assertIn(self.two_month_old_login_group, filtered_qs)
        self.assertIn(self.not_yet_logged_in_group, filtered_qs)

    def test_one_week_ago_filter(self):
        f = LastManagerLoginFilter(
            None,
            {"last_manager_login": "1_week_ago"},
            SupportGroup,
            admin.SupportGroupAdmin,
        )
        filtered_qs = f.queryset(None, SupportGroup.objects.all())
        self.assertNotIn(self.recently_logged_in_group, filtered_qs)
        self.assertIn(self.one_month_old_login_group, filtered_qs)
        self.assertIn(self.two_month_old_login_group, filtered_qs)
        self.assertIn(self.not_yet_logged_in_group, filtered_qs)

    def test_one_month_ago_filter(self):
        f = LastManagerLoginFilter(
            None,
            {"last_manager_login": "1_month_ago"},
            SupportGroup,
            admin.SupportGroupAdmin,
        )
        filtered_qs = f.queryset(None, SupportGroup.objects.all())
        self.assertNotIn(self.recently_logged_in_group, filtered_qs)
        self.assertIn(self.one_month_old_login_group, filtered_qs)
        self.assertIn(self.two_month_old_login_group, filtered_qs)
        self.assertIn(self.not_yet_logged_in_group, filtered_qs)

    def test_two_month_ago_filter(self):
        f = LastManagerLoginFilter(
            None,
            {"last_manager_login": "2_month_ago"},
            SupportGroup,
            admin.SupportGroupAdmin,
        )
        filtered_qs = f.queryset(None, SupportGroup.objects.all())
        self.assertNotIn(self.recently_logged_in_group, filtered_qs)
        self.assertNotIn(self.one_month_old_login_group, filtered_qs)
        self.assertIn(self.two_month_old_login_group, filtered_qs)
        self.assertIn(self.not_yet_logged_in_group, filtered_qs)

    def test_three_month_ago_filter(self):
        f = LastManagerLoginFilter(
            None,
            {"last_manager_login": "3_month_ago"},
            SupportGroup,
            admin.SupportGroupAdmin,
        )
        filtered_qs = f.queryset(None, SupportGroup.objects.all())
        self.assertNotIn(self.recently_logged_in_group, filtered_qs)
        self.assertNotIn(self.one_month_old_login_group, filtered_qs)
        self.assertNotIn(self.two_month_old_login_group, filtered_qs)
        self.assertIn(self.not_yet_logged_in_group, filtered_qs)

    def test_exact_date_ago_filter(self):
        f = LastManagerLoginFilter(
            None,
            {
                "last_manager_login": (timezone.now() - relativedelta(days=36))
                .date()
                .strftime("%Y-%m-%d")
            },
            SupportGroup,
            admin.SupportGroupAdmin,
        )
        filtered_qs = f.queryset(None, SupportGroup.objects.all())
        self.assertNotIn(self.recently_logged_in_group, filtered_qs)
        self.assertNotIn(self.one_month_old_login_group, filtered_qs)
        self.assertIn(self.two_month_old_login_group, filtered_qs)
        self.assertIn(self.not_yet_logged_in_group, filtered_qs)
