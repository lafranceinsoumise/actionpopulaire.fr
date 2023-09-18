import uuid
from unittest.mock import patch

from django.utils import timezone
from rest_framework.test import APITestCase

from agir.donations.models import SpendingRequest, Operation
from agir.groups.models import SupportGroup, Membership, SupportGroupExternalLink
from agir.lib.tests.mixins import create_membership
from agir.people.models import Person


class GroupJoinAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            email="person@example.com", create_role=True, is_political_support=True
        )

    def test_anonymous_person_cannot_join(self):
        self.client.logout()
        group = SupportGroup.objects.create()
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 401)

    def test_person_cannot_join_closed_group(self):
        self.client.force_login(self.person.role)
        closed_group = SupportGroup.objects.create(
            type=SupportGroup.TYPE_LOCAL_GROUP, open=False
        )
        res = self.client.post(f"/api/groupes/{closed_group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("error_code", res.data)

    # (Temporarily disabled)
    # def test_person_cannot_join_full_group(self):
    #     self.client.force_login(self.person.role)
    #     full_group = SupportGroup.objects.create(type=SupportGroup.TYPE_LOCAL_GROUP)
    #     for i in range(SupportGroup.MEMBERSHIP_LIMIT + 1):
    #         member = Person.objects.create_person(email=f"member_{i}@example.com")
    #         Membership.objects.create(
    #             supportgroup=full_group,
    #             person=member,
    #             membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
    #         )
    #     res = self.client.post(f"/api/groupes/{full_group.pk}/rejoindre/")
    #     self.assertEqual(res.status_code, 405)
    #     self.assertIn("error_code", res.data)
    #     self.assertEqual(res.data["error_code"], res.data)

    def test_no_content_response_if_already_member(self):
        person_group = SupportGroup.objects.create()
        Membership.objects.create(
            supportgroup=person_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/groupes/{person_group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 204)

    def test_ok_response_if_already_follower(self):
        person_group = SupportGroup.objects.create()
        membership = Membership.objects.create(
            supportgroup=person_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/groupes/{person_group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 200)
        membership.refresh_from_db()
        self.assertEqual(membership.membership_type, Membership.MEMBERSHIP_TYPE_MEMBER)

    def test_authenticated_person_can_join_available_group(self):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 201)

    def test_membership_is_created_upoin_joining(self):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        self.assertFalse(
            Membership.objects.filter(person=self.person, supportgroup=group).exists()
        )
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(
            Membership.objects.filter(person=self.person, supportgroup=group).exists()
        )

    @patch("agir.groups.views.api_views.someone_joined_notification")
    def test_someone_joined_notification_is_sent_upon_joining(
        self, someone_joined_notification
    ):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        someone_joined_notification.assert_not_called()
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 201)
        someone_joined_notification.assert_called()


class GroupFollowAPITestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            email="person@example.com", create_role=True, is_political_support=True
        )

    def test_anonymous_person_cannot_follow(self):
        self.client.logout()
        group = SupportGroup.objects.create()
        res = self.client.post(f"/api/groupes/{group.pk}/suivre/")
        self.assertEqual(res.status_code, 401)

    def test_person_cannot_follow_closed_group(self):
        self.client.force_login(self.person.role)
        closed_group = SupportGroup.objects.create(
            type=SupportGroup.TYPE_LOCAL_GROUP, open=False
        )
        res = self.client.post(f"/api/groupes/{closed_group.pk}/suivre/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("error_code", res.data)

    # (Temporarily disabled)
    # def test_person_can_follow_full_group(self):
    #     self.client.force_login(self.person.role)
    #     full_group = SupportGroup.objects.create(type=SupportGroup.TYPE_LOCAL_GROUP)
    #     for i in range(SupportGroup.MEMBERSHIP_LIMIT + 1):
    #         member = Person.objects.create_person(email=f"member_{i}@example.com")
    #         Membership.objects.create(
    #             supportgroup=full_group,
    #             person=member,
    #             membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
    #         )
    #     res = self.client.post(f"/api/groupes/{full_group.pk}/suivre/")
    #     self.assertEqual(res.status_code, 200)

    def test_no_content_response_if_already_follower(self):
        person_group = SupportGroup.objects.create()
        Membership.objects.create(
            supportgroup=person_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/groupes/{person_group.pk}/suivre/")
        self.assertEqual(res.status_code, 204)

    def test_ok_response_if_already_member(self):
        person_group = SupportGroup.objects.create()
        membership = Membership.objects.create(
            supportgroup=person_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/groupes/{person_group.pk}/suivre/")
        self.assertEqual(res.status_code, 200)
        membership.refresh_from_db()
        self.assertEqual(
            membership.membership_type, Membership.MEMBERSHIP_TYPE_FOLLOWER
        )

    def test_authenticated_person_can_follow_group(self):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        res = self.client.post(f"/api/groupes/{group.pk}/suivre/")
        self.assertEqual(res.status_code, 201)

    def test_membership_is_created_upoin_following(self):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        self.assertFalse(
            Membership.objects.filter(person=self.person, supportgroup=group).exists()
        )
        res = self.client.post(f"/api/groupes/{group.pk}/suivre/")
        self.assertEqual(res.status_code, 201)
        self.assertTrue(
            Membership.objects.filter(person=self.person, supportgroup=group).exists()
        )

    @patch("agir.groups.views.api_views.someone_joined_notification")
    def test_someone_joined_notification_is_sent_upon_joining(
        self, someone_joined_notification
    ):
        group = SupportGroup.objects.create()
        self.client.force_login(self.person.role)
        someone_joined_notification.assert_not_called()
        res = self.client.post(f"/api/groupes/{group.pk}/rejoindre/")
        self.assertEqual(res.status_code, 201)
        someone_joined_notification.assert_called()


class QuitGroupAPITestCase(APITestCase):
    def setUp(self):
        self.member = Person.objects.create_person(
            email="member@example.com",
            create_role=True,
        )
        self.first_ref = Person.objects.create_person(
            email="referent@example.com",
            create_role=True,
        )
        self.group = SupportGroup.objects.create()
        self.membership = Membership.objects.create(
            person=self.member,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        Membership.objects.create(
            person=self.first_ref,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

    def test_anonymous_person_cannot_quit_group(self):
        self.client.logout()
        res = self.client.delete(f"/api/groupes/{self.group.pk}/quitter/")
        self.assertEqual(res.status_code, 401)

    def test_non_member_cannot_quit_group(self):
        non_member = Person.objects.create_person(
            email="non_member@example.com",
            create_role=True,
        )
        self.client.force_login(non_member.role)
        res = self.client.delete(f"/api/groupes/{self.group.pk}/quitter/")
        self.assertEqual(res.status_code, 404)

    def test_last_referent_cannot_quit_group(self):
        self.assertEqual(
            Membership.objects.filter(
                supportgroup=self.group,
                membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
            ).count(),
            1,
        )
        self.client.force_login(self.first_ref.role)
        res = self.client.delete(f"/api/groupes/{self.group.pk}/quitter/")
        self.assertEqual(res.status_code, 403)
        self.assertIn("error_code", res.data)
        self.assertEqual(res.data["error_code"], "group_last_referent")
        self.assertEqual(
            Membership.objects.filter(
                supportgroup=self.group,
                membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
            ).count(),
            1,
        )

    def test_non_last_referent_can_quit_group(self):
        second_ref = Person.objects.create_person(
            email="second_ref@example.com",
            create_role=True,
        )
        Membership.objects.create(
            person=second_ref,
            supportgroup=self.group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        self.assertEqual(
            Membership.objects.filter(
                supportgroup=self.group,
                membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
            ).count(),
            2,
        )
        self.client.force_login(second_ref.role)
        res = self.client.delete(f"/api/groupes/{self.group.pk}/quitter/")
        self.assertEqual(res.status_code, 204)
        self.assertEqual(
            Membership.objects.filter(
                supportgroup=self.group,
                membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
            ).count(),
            1,
        )

    def test_member_can_quit_group(self):
        self.assertEqual(
            Membership.objects.filter(
                supportgroup=self.group,
                person=self.member,
            ).count(),
            1,
        )
        self.client.force_login(self.member.role)
        res = self.client.delete(f"/api/groupes/{self.group.pk}/quitter/")
        self.assertEqual(res.status_code, 204)
        self.assertEqual(
            Membership.objects.filter(
                supportgroup=self.group,
                person=self.member,
            ).count(),
            0,
        )


class GroupUpdateAPIViewTestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create(name="group Test")
        self.simple_member = Person.objects.create_person(
            email="simple_member@agir.local", create_role=True
        )
        self.referent_member = Person.objects.create_person(
            email="referent@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.simple_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.referent_member,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        self.valid_data = {"name": "Groupe de Test", "description": "New Desc"}

    def test_anonymous_person_cannot_update(self):
        self.client.logout()
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/", data=self.valid_data
        )
        self.assertEqual(res.status_code, 401)

    def test_simple_members_cannot_update(self):
        self.client.force_login(self.simple_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/", data=self.valid_data
        )
        self.assertEqual(res.status_code, 403)

    def test_group_does_not_exist(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.patch(
            f"/api/groupes/{uuid.uuid4()}/update/", data=self.valid_data
        )
        self.assertEqual(res.status_code, 404)

    def test_manager_can_update(self):
        self.assertNotEqual(self.group.name, self.valid_data["name"])
        self.client.force_login(self.referent_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/", data=self.valid_data
        )
        self.assertEqual(res.status_code, 200)
        self.group.refresh_from_db()
        self.assertEqual(self.group.name, self.valid_data["name"])

    def test_invalid_name(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/",
            data={**self.valid_data, "name": ""},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("name", res.data)

    def test_invalid_description(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/",
            data={**self.valid_data, "description": None},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("description", res.data)

    def test_invalid_image(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/",
            data={**self.valid_data, "image": "TEXTE"},
        )
        self.assertEqual(res.status_code, 422)
        self.assertIn("image", res.data)

    @patch("agir.groups.serializers.send_support_group_changed_notification.delay")
    def notification_was_sent(self, send_support_group_changed):
        send_support_group_changed.assert_not_called()
        self.client.force_login(self.referent_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/", data=self.valid_data
        )
        self.assertEqual(res.status_code, 200)
        send_support_group_changed.assert_called()
        args = send_support_group_changed.call_args
        self.assertEqual(args[0][0], self.group.pk)
        self.assertEqual(args[0][1], self.valid_data)

    @patch("agir.groups.serializers.geocode_support_group.delay")
    def geolocation_was_updated(self, geocode_support_group):
        geocode_support_group.assert_not_called()
        self.client.force_login(self.referent_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/", data={"location": {"zip": "75001"}}
        )
        self.assertEqual(res.status_code, 200)
        geocode_support_group.assert_called()
        args = send_support_group_changed.call_args
        self.assertEqual(args[0][0], self.group.pk)

    @patch("agir.groups.serializers.geocode_support_group.delay")
    def group_was_updated_without_location(self, geocode_support_group):
        geocode_support_group.assert_not_called()
        self.client.force_login(self.referent_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/update/",
            data={"name": "Nom de groupe different"},
        )
        self.assertEqual(res.status_code, 200)
        geocode_support_group.assert_not_called()


class GroupInvitationAPIViewTestCase(APITestCase):
    def setUp(self):
        self.valid_email = "moi@france.fr"
        self.wrong_email = "faux@france"
        self.group = SupportGroup.objects.create(name="group Test")
        self.simple_member = Person.objects.create_person(
            email="simple_member@agir.local", create_role=True
        )
        self.referent_member = Person.objects.create_person(
            email="referent@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.simple_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.referent_member,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

    def test_anonymous_person_cannot_invite(self):
        self.client.logout()
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/invitation/",
            data={"email": self.valid_email},
        )
        self.assertEqual(res.status_code, 401)

    def test_simple_members_cannot_invite(self):
        self.client.force_login(self.simple_member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/invitation/",
            data={"email": self.valid_email},
        )
        self.assertEqual(res.status_code, 403)

    def test_invitation_group_inexistant(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.post(
            f"/api/groupes/{uuid.uuid4()}/invitation/", data={"email": self.valid_email}
        )
        self.assertEqual(res.status_code, 404)

    def test_invitation_wrong_email(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/invitation/",
            data={"email": self.wrong_email},
        )
        self.assertEqual(res.status_code, 422)

    def test_invitation_empty_email(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/invitation/",
            data={"email": ""},
        )
        self.assertEqual(res.status_code, 422)

    def test_invitation_mail_already_exist(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/invitation/",
            data={"email": self.simple_member.email},
        )
        self.assertEqual(res.status_code, 422)

    def test_invitation_valid_email(self):
        self.client.force_login(self.referent_member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/invitation/",
            data={"email": self.valid_email},
        )
        self.assertEqual(res.status_code, 201)

    @patch("agir.groups.views.api_views.invite_to_group.delay")
    def test_invitation_was_sent(self, invite_to_group):
        self.client.force_login(self.referent_member.role)
        invite_to_group.assert_not_called()
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/invitation/",
            data={"email": self.valid_email},
        )
        invite_to_group.assert_called()
        self.assertEqual(res.status_code, 201)


class GroupFinanceAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create(name="group Test")
        self.simple_member = Person.objects.create_person(
            email="simple_member@agir.local", create_role=True
        )
        self.manager_member = Person.objects.create_person(
            email="manager@agir.local", create_role=True
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.simple_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        Membership.objects.create(
            supportgroup=self.group,
            person=self.manager_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.donation_operation = Operation.objects.create(group=self.group, amount=10)
        self.spending_request = SpendingRequest.objects.create(
            group=self.group,
            title="Ma demande de dépense",
            event=None,
            category=SpendingRequest.Category.HARDWARE.value,
            category_precisions="Super truc trop cool",
            explanation="On en a VRAIMENT VRAIMENT besoin.",
            spending_date=timezone.now(),
            bank_account_name="Super CLIENT",
            bank_account_iban="FR65 0382 9038 7327 9323 466",
            bank_account_bic="",
            amount=8500,
        )

    def test_anonymous_person_cannot_view_group_finance(self):
        self.client.logout()
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/finance/",
        )
        self.assertEqual(res.status_code, 401)

    def test_group_member_cannot_view_group_finance(self):
        self.client.force_login(self.simple_member.role)
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/finance/",
        )
        self.assertEqual(res.status_code, 403)

    def test_group_manager_can_view_group_finance(self):
        self.client.force_login(self.manager_member.role)
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/finance/",
        )
        self.assertEqual(res.status_code, 200)

    def test_api_response_contains_a_donation_property(self):
        self.client.force_login(self.manager_member.role)
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/finance/",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("donation", res.data)
        self.assertEqual(res.data["donation"], 10)

    def test_api_response_contains_the_list_of_the_group_spending_requests(self):
        self.client.force_login(self.manager_member.role)
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/finance/",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("spendingRequests", res.data)
        self.assertEqual(len(res.data["spendingRequests"]), 1)


class GroupExternalLinkAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create(name="group Test")

        self.non_member = Person.objects.create_person(
            email="non_member@agir.local", create_role=True
        )
        self.simple_member = Person.objects.create_person(
            email="simple_member@agir.local", create_role=True
        )
        self.manager_member = Person.objects.create_person(
            email="manager@agir.local", create_role=True
        )

        Membership.objects.create(
            supportgroup=self.group,
            person=self.simple_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        Membership.objects.create(
            supportgroup=self.group,
            person=self.manager_member,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.external_link = SupportGroupExternalLink.objects.create(
            url="http://agir.local", label="AP", supportgroup=self.group
        )

        self.valid_data = {
            "url": "http://agir.local",
            "label": "AP",
        }

    def test_anonymous_can_retrieve_a_link(self):
        self.client.logout()
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("url", res.data)
        self.assertIn("label", res.data)

    def test_non_group_member_can_retrieve_a_link(self):
        self.client.force_login(self.non_member.role)
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("url", res.data)
        self.assertIn("label", res.data)

    def test_group_member_can_retrieve_a_link(self):
        self.client.force_login(self.simple_member.role)
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("url", res.data)
        self.assertIn("label", res.data)

    def test_group_manager_can_retrieve_a_link(self):
        self.client.force_login(self.manager_member.role)
        res = self.client.get(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("url", res.data)
        self.assertIn("label", res.data)

    def test_anonymous_cannot_add_a_link(self):
        self.client.logout()
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/link/",
            data=self.valid_data,
        )
        self.assertEqual(res.status_code, 401)

    def test_non_group_member_cannot_add_a_link(self):
        self.client.force_login(self.non_member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/link/",
            data=self.valid_data,
        )
        self.assertEqual(res.status_code, 403)

    def test_group_member_cannot_add_a_link(self):
        self.client.force_login(self.simple_member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/link/",
            data=self.valid_data,
        )
        self.assertEqual(res.status_code, 403)

    def test_group_manager_can_add_a_link(self):
        self.client.force_login(self.manager_member.role)
        res = self.client.post(
            f"/api/groupes/{self.group.pk}/link/",
            data=self.valid_data,
        )
        self.assertEqual(res.status_code, 201)
        self.assertIn("url", res.data)
        self.assertIn("label", res.data)

    def test_anonymous_cannot_update_a_link(self):
        self.client.logout()
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/",
            data=self.valid_data,
        )
        self.assertEqual(res.status_code, 401)

    def test_non_group_member_cannot_update_a_link(self):
        self.client.force_login(self.non_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/",
            data=self.valid_data,
        )
        self.assertEqual(res.status_code, 403)

    def test_group_member_cannot_update_a_link(self):
        self.client.force_login(self.simple_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/",
            data=self.valid_data,
        )
        self.assertEqual(res.status_code, 403)

    def test_group_manager_can_update_a_link(self):
        self.client.force_login(self.manager_member.role)
        res = self.client.patch(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/",
            data=self.valid_data,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("url", res.data)
        self.assertIn("label", res.data)

    def test_anonymous_cannot_delete_a_link(self):
        self.client.logout()
        res = self.client.delete(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/"
        )
        self.assertEqual(res.status_code, 401)

    def test_non_group_member_cannot_delete_a_link(self):
        self.client.force_login(self.non_member.role)
        res = self.client.delete(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/"
        )
        self.assertEqual(res.status_code, 403)

    def test_group_member_cannot_delete_a_link(self):
        self.client.force_login(self.simple_member.role)
        res = self.client.delete(
            f"/api/groupes/{self.group.pk}/link/{self.external_link.pk}/"
        )
        self.assertEqual(res.status_code, 403)

    def test_group_manager_can_delete_a_link(self):
        self.client.force_login(self.manager_member.role)
        pk = self.external_link.pk
        res = self.client.delete(f"/api/groupes/{self.group.pk}/link/{pk}/")
        self.assertEqual(res.status_code, 204)
        res = self.client.get(f"/api/groupes/{self.group.pk}/link/{pk}/")
        self.assertEqual(res.status_code, 404)


class GroupMembershipUpdateAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create(name="Group")
        self.non_member = Person.objects.create_person(
            email="non_member@agir.local", create_role=True
        )
        self.follower = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER
        ).person
        self.member = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
        ).person
        self.referent = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_REFERENT
        ).person
        self.manager = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_MANAGER
        ).person
        self.target = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
        )

    def test_only_referents_and_managers_can_set_follower_to_member(self):
        data = {"membershipType": Membership.MEMBERSHIP_TYPE_MEMBER}
        self.target.membership_type = Membership.MEMBERSHIP_TYPE_FOLLOWER
        self.target.save()
        # Anonymous
        self.client.logout()
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 401)
        # Non member
        self.client.force_login(user=self.non_member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Follower
        self.client.force_login(user=self.follower.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Member
        self.client.force_login(user=self.member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Manager
        self.client.force_login(user=self.manager.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 200)
        # Referent
        self.client.force_login(user=self.referent.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 200)

    def test_only_referents_can_change_a_referent_membership_type(self):
        data = {"membershipType": Membership.MEMBERSHIP_TYPE_MANAGER}
        self.target.membership_type = Membership.MEMBERSHIP_TYPE_REFERENT
        self.target.save()
        # Anonymous
        self.client.logout()
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 401)
        # Non member
        self.client.force_login(user=self.non_member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Follower
        self.client.force_login(user=self.follower.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Member
        self.client.force_login(user=self.member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Manager
        self.client.force_login(user=self.manager.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Referent
        self.client.force_login(user=self.referent.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 200)

    def test_only_referents_can_change_a_manager_membership_type(self):
        data = {"membershipType": Membership.MEMBERSHIP_TYPE_REFERENT}
        self.target.membership_type = Membership.MEMBERSHIP_TYPE_MANAGER
        self.target.save()
        # Anonymous
        self.client.logout()
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 401)
        # Non member
        self.client.force_login(user=self.non_member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Follower
        self.client.force_login(user=self.follower.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Member
        self.client.force_login(user=self.member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Manager
        self.client.force_login(user=self.manager.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Referent
        self.client.force_login(user=self.referent.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 200)

    def test_only_referents_can_set_referents(self):
        data = {"membershipType": Membership.MEMBERSHIP_TYPE_REFERENT}
        self.target.membership_type = Membership.MEMBERSHIP_TYPE_MEMBER
        self.target.save()
        # Anonymous
        self.client.logout()
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 401)
        # Non member
        self.client.force_login(user=self.non_member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Follower
        self.client.force_login(user=self.follower.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Member
        self.client.force_login(user=self.member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Manager
        self.client.force_login(user=self.manager.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Referent
        self.client.force_login(user=self.referent.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 200)

    def test_only_referents_can_set_managers(self):
        data = {"membershipType": Membership.MEMBERSHIP_TYPE_MANAGER}
        self.target.membership_type = Membership.MEMBERSHIP_TYPE_MEMBER
        self.target.save()
        # Anonymous
        self.client.logout()
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 401)
        # Non member
        self.client.force_login(user=self.non_member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Follower
        self.client.force_login(user=self.follower.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Member
        self.client.force_login(user=self.member.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Manager
        self.client.force_login(user=self.manager.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 403)
        # Referent
        self.client.force_login(user=self.referent.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 200)

    def test_cannot_set_more_than_two_referents_for_a_group(self):
        group = SupportGroup.objects.create(name="G")
        a_member = create_membership(
            supportgroup=group, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
        )
        another_member = create_membership(
            supportgroup=group, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
        )
        the_first_referent = create_membership(
            supportgroup=group, membership_type=Membership.MEMBERSHIP_TYPE_REFERENT
        )
        data = {"membershipType": Membership.MEMBERSHIP_TYPE_REFERENT}
        self.client.force_login(user=the_first_referent.person.role)
        res = self.client.patch(f"/api/groupes/membres/{a_member.id}/", data=data)
        self.assertEqual(res.status_code, 200)
        res = self.client.patch(f"/api/groupes/membres/{another_member.id}/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("membershipType", res.data)

    @patch("agir.groups.serializers.member_to_follower_notification")
    def test_notification_is_sent_for_member_to_follower_change(
        self, member_to_follower_notification
    ):
        data = {"membershipType": Membership.MEMBERSHIP_TYPE_MEMBER}
        self.target.membership_type = Membership.MEMBERSHIP_TYPE_FOLLOWER
        self.target.save()
        member_to_follower_notification.assert_not_called()
        self.client.force_login(user=self.referent.role)
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 200)
        member_to_follower_notification.assert_not_called()
        data = {"membershipType": Membership.MEMBERSHIP_TYPE_FOLLOWER}
        res = self.client.patch(f"/api/groupes/membres/{self.target.id}/", data=data)
        self.assertEqual(res.status_code, 200)
        member_to_follower_notification.assert_called()


class MemberPersonalInformationAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create(name="Group")
        self.non_member = Person.objects.create_person(
            email="non_member@agir.local", create_role=True
        )
        self.follower = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER
        ).person
        self.member = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
        ).person
        self.referent = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_REFERENT
        ).person
        self.manager = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_MANAGER
        ).person
        self.target = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
        )

    def test_only_referents_and_managers_can_access_member_personal_info(self):
        # Anonymous
        self.client.logout()
        res = self.client.get(f"/api/groupes/membres/{self.target.id}/informations/")
        self.assertEqual(res.status_code, 401)
        # Non member
        self.client.force_login(user=self.non_member.role)
        res = self.client.get(f"/api/groupes/membres/{self.target.id}/informations/")
        self.assertEqual(res.status_code, 403)
        # Follower
        self.client.force_login(user=self.follower.role)
        res = self.client.get(f"/api/groupes/membres/{self.target.id}/informations/")
        self.assertEqual(res.status_code, 403)
        # Member
        self.client.force_login(user=self.member.role)
        res = self.client.get(f"/api/groupes/membres/{self.target.id}/informations/")
        self.assertEqual(res.status_code, 403)
        # Manager
        self.client.force_login(user=self.manager.role)
        res = self.client.get(f"/api/groupes/membres/{self.target.id}/informations/")
        self.assertEqual(res.status_code, 200)
        # Referent
        self.client.force_login(user=self.referent.role)
        res = self.client.get(f"/api/groupes/membres/{self.target.id}/informations/")
        self.assertEqual(res.status_code, 200)

    def test_restricted_information_are_not_accessible_without_member_consent(self):
        restricted_fields = [
            "firstName",
            "lastName",
            "gender",
            "phone",
            "address",
            "isPoliticalSupport",
            "isLiaison",
            "hasGroupNotifications",
        ]
        self.target.personal_information_sharing_consent = False
        self.target.save()
        self.client.force_login(user=self.referent.role)

        res = self.client.get(f"/api/groupes/membres/{self.target.id}/informations/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("id", res.data)
        for field in restricted_fields:
            self.assertNotIn(field, res.data)

        self.target.personal_information_sharing_consent = True
        self.target.save()
        res = self.client.get(f"/api/groupes/membres/{self.target.id}/informations/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("id", res.data)
        for field in restricted_fields:
            self.assertIn(field, res.data)


class UpdateOwnMembershipAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create(name="Group")
        self.non_member = Person.objects.create_person(
            email="non_member@agir.local", create_role=True
        )
        self.member = create_membership(
            supportgroup=self.group, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER
        )

    def test_anonymous_cannot_update_membership(self):
        self.client.logout()
        data = {"personalInfoConsent": True}
        res = self.client.patch(f"/api/groupes/{self.group.id}/membre/", data=data)
        self.assertEqual(res.status_code, 401)

    def test_non_member_cannot_update_membership(self):
        self.client.force_login(self.non_member.role)
        data = {"personalInfoConsent": True}
        res = self.client.patch(f"/api/groupes/{self.group.id}/membre/", data=data)
        self.assertEqual(res.status_code, 404)

    def test_member_cannot_update_own_membership(self):
        self.member.personal_info_sharing_consent = None
        self.member.save()
        self.member.refresh_from_db()
        self.assertIsNone(self.member.personal_information_sharing_consent)
        self.client.force_login(self.member.person.role)
        data = {"personalInfoConsent": True}
        res = self.client.patch(f"/api/groupes/{self.group.id}/membre/", data=data)
        self.assertEqual(res.status_code, 200)
        self.member.refresh_from_db()
        self.assertTrue(self.member.personal_information_sharing_consent)
        data = {"personalInfoConsent": False}
        res = self.client.patch(f"/api/groupes/{self.group.id}/membre/", data=data)
        self.assertEqual(res.status_code, 200)
        self.member.refresh_from_db()
        self.assertFalse(self.member.personal_information_sharing_consent)
