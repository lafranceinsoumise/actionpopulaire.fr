from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from agir.groups import rules
from agir.groups.models import SupportGroup, Membership
from agir.people.models import Person


class GroupRulesTestCase(TestCase):
    def setUp(self) -> None:
        self.person = Person.objects.create_insoumise(
            "test@agir.local", create_role=True
        )
        self.group1 = SupportGroup.objects.create(name="Groupe 1")
        self.membership1 = Membership.objects.create(
            person=self.person,
            supportgroup=self.group1,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        self.group2 = SupportGroup.objects.create(name="Groupe 2")
        self.membership2 = Membership.objects.create(
            person=self.person,
            supportgroup=self.group2,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

    def test_is_published(self):
        self.group1.published = True
        self.group1.save()

        self.group2.published = False
        self.group2.save()

        self.assertTrue(rules.is_published_group(None, self.group1))
        self.assertTrue(rules.is_published_group(self.person.role, self.group1))

        self.assertFalse(rules.is_published_group(None, self.group2))
        self.assertFalse(rules.is_published_group(self.person.role, self.group2))

    def test_is_editable(self):
        self.group1.editable = True
        self.group1.save()

        self.group2.editable = False
        self.group2.save()

        self.assertTrue(rules.is_editable_group(None, self.group1))
        self.assertTrue(rules.is_editable_group(self.person.role, self.group1))

        self.assertFalse(rules.is_editable_group(None, self.group2))
        self.assertFalse(rules.is_editable_group(self.person.role, self.group2))

    def test_has_manager_rights(self):
        self.membership2.membership_type = Membership.MEMBERSHIP_TYPE_MANAGER
        self.membership2.save()

        self.assertFalse(rules.is_at_least_manager_for_group(self.person.role, None))
        self.assertFalse(
            rules.is_at_least_manager_for_group(self.person.role, self.group1)
        )
        self.assertTrue(
            rules.is_at_least_manager_for_group(self.person.role, self.group2)
        )

        self.membership1.membership_type = Membership.MEMBERSHIP_TYPE_REFERENT
        self.membership1.save()

        self.assertTrue(
            rules.is_at_least_manager_for_group(self.person.role, self.group1)
        )


class SupportGroupPermissionsTestCase(TestCase):
    def setUp(self) -> None:
        self.group = SupportGroup.objects.create(name="Group", published=True)

        self.referent = Person.objects.create_insoumise(
            "animateur@agir.local", create_role=True
        )
        self.manager = Person.objects.create_insoumise(
            "gestionnaire@agir.local", create_role=True
        )
        self.member = Person.objects.create_insoumise(
            "membre@agir.local", create_role=True
        )
        self.follower = Person.objects.create_insoumise(
            "abonnee@agir.local", create_role=True
        )
        self.outsider = Person.objects.create_insoumise(
            "outsider@agir.local", create_role=True
        )

        self.anonymous = AnonymousUser()

        self.referent_membership = Membership.objects.create(
            supportgroup=self.group,
            person=self.referent,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        self.manager_membership = Membership.objects.create(
            supportgroup=self.group,
            person=self.manager,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.member_membership = Membership.objects.create(
            supportgroup=self.group,
            person=self.member,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        self.follower_membership = Membership.objects.create(
            supportgroup=self.group,
            person=self.follower,
            membership_type=Membership.MEMBERSHIP_TYPE_FOLLOWER,
        )

    def test_can_view_published_group(self):
        self.assertTrue(self.referent.has_perm("groups.view_supportgroup", self.group))
        self.assertTrue(self.manager.has_perm("groups.view_supportgroup", self.group))
        self.assertTrue(self.member.has_perm("groups.view_supportgroup", self.group))
        self.assertTrue(self.follower.has_perm("groups.view_supportgroup", self.group))
        self.assertTrue(self.outsider.has_perm("groups.view_supportgroup", self.group))
        self.assertTrue(self.anonymous.has_perm("groups.view_supportgroup", self.group))

    def test_cannot_view_unpublished_group(self):
        self.group.published = False
        self.group.save()

        self.assertFalse(self.referent.has_perm("groups.view_supportgroup", self.group))
        self.assertFalse(self.manager.has_perm("groups.view_supportgroup", self.group))
        self.assertFalse(self.member.has_perm("groups.view_supportgroup", self.group))
        self.assertFalse(self.follower.has_perm("groups.view_supportgroup", self.group))
        self.assertFalse(self.outsider.has_perm("groups.view_supportgroup", self.group))
        self.assertFalse(
            self.anonymous.has_perm("groups.view_supportgroup", self.group)
        )

    def test_only_managers_can_change_group(self):
        self.assertTrue(
            self.referent.has_perm("groups.change_supportgroup", self.group)
        )
        self.assertTrue(self.manager.has_perm("groups.change_supportgroup", self.group))
        self.assertFalse(self.member.has_perm("groups.change_supportgroup", self.group))
        self.assertFalse(
            self.follower.has_perm("groups.change_supportgroup", self.group)
        )
        self.assertFalse(
            self.outsider.has_perm("groups.change_supportgroup", self.group)
        )
        self.assertFalse(
            self.anonymous.has_perm("groups.change_supportgroup", self.group)
        )

    def test_only_referent_cannot_leave_group(self):
        self.assertFalse(
            self.referent.has_perm("groups.delete_membership", self.referent_membership)
        )
        self.assertTrue(
            self.manager.has_perm("groups.delete_membership", self.manager_membership)
        )
        self.assertTrue(
            self.member.has_perm("groups.delete_membership", self.member_membership)
        )
        self.assertTrue(
            self.follower.has_perm("groups.delete_membership", self.follower_membership)
        )

        self.manager_membership.membership_type = Membership.MEMBERSHIP_TYPE_REFERENT
        self.manager_membership.save()

        self.assertTrue(
            self.referent.has_perm("groups.delete_membership", self.referent_membership)
        )

    def test_only_referent_can_add_manager(self):
        self.assertTrue(
            self.referent.has_perm("groups.add_manager_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.manager.has_perm("groups.add_manager_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.member.has_perm("groups.add_manager_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.follower.has_perm("groups.add_manager_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.outsider.has_perm("groups.add_manager_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.anonymous.has_perm("groups.add_manager_to_supportgroup", self.group)
        )

    def test_only_referent_can_add_referent_if_he_is_only_referent(self):
        self.assertTrue(
            self.referent.has_perm("groups.add_referent_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.manager.has_perm("groups.add_referent_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.member.has_perm("groups.add_referent_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.follower.has_perm("groups.add_referent_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.outsider.has_perm("groups.add_referent_to_supportgroup", self.group)
        )
        self.assertFalse(
            self.anonymous.has_perm("groups.add_referent_to_supportgroup", self.group)
        )

        self.manager_membership.membership_type = Membership.MEMBERSHIP_TYPE_REFERENT
        self.manager_membership.save()

        self.assertFalse(
            self.referent.has_perm("groups.add_referent_to_supportgroup", self.group)
        )
