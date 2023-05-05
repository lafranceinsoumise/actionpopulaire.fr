from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from agir.people.models import Person
from ..models import SupportGroup, Membership, SupportGroupSubtype
from ..utils.certification import check_certification_criteria
from ..utils.supportgroup import (
    DAYS_SINCE_GROUP_CREATION_LIMIT,
    DAYS_SINCE_LAST_EVENT_LIMIT,
    is_active_group_filter,
)
from ...events.models import Event, OrganizerConfig


class IsActiveGroupFilterTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "person@agir.test", create_role=True
        )
        self.client.force_login(self.person.role)
        self.now = timezone.now()
        self.older_than_limit_date = self.now - timedelta(
            days=DAYS_SINCE_LAST_EVENT_LIMIT + 10
        )

    def create_group(self, *args, is_new=True, **kwargs):
        if not is_new:
            kwargs["created"] = timezone.now() - timedelta(
                days=DAYS_SINCE_GROUP_CREATION_LIMIT
            )
        group = SupportGroup.objects.create(*args, **kwargs)
        Membership.objects.create(person=self.person, supportgroup=group)
        return group

    def create_group_event(self, group, start_time=timezone.now()):
        event = Event.objects.create(
            name="événement test pour groupe",
            start_time=start_time,
            end_time=start_time + timezone.timedelta(hours=1),
        )
        OrganizerConfig.objects.create(event=event, person=self.person, as_group=group)
        return event

    def assert_group_in_queryset(self, group):
        group_pks = list(
            SupportGroup.objects.filter(is_active_group_filter()).values_list(
                "pk", flat=True
            )
        )
        self.assertIn(group.pk, group_pks)

    def assert_group_not_in_queryset(self, group):
        group_pks = list(
            SupportGroup.objects.filter(is_active_group_filter()).values_list(
                "pk", flat=True
            )
        )
        self.assertNotIn(group.pk, group_pks)

    def test_new_group_in_queryset(self):
        new_group = self.create_group(name="New group", is_new=True)
        self.create_group_event(group=new_group, start_time=self.older_than_limit_date)
        self.assert_group_in_queryset(new_group)

    def test_active_group_in_queryset(self):
        active_group = self.create_group(name="Active group", is_new=False)
        self.create_group_event(
            group=active_group, start_time=self.older_than_limit_date
        )
        self.create_group_event(group=active_group, start_time=self.now)
        self.assert_group_in_queryset(active_group)

    def test_inactive_group_not_in_queryset(self):
        inactive_group = self.create_group(name="Inactive group", is_new=False)
        self.assert_group_not_in_queryset(inactive_group)
        self.create_group_event(
            group=inactive_group, start_time=self.older_than_limit_date
        )
        self.assert_group_not_in_queryset(inactive_group)


class SupportGroupCertificationCriteriaTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create("person@agir.test", create_role=True)

    def test_supportgroup_creation(self):
        group = SupportGroup.objects.create(name="G")
        criteria = check_certification_criteria(group)
        self.assertFalse(criteria["creation"])
        group.created = timezone.now() - timedelta(days=32)
        group.save()
        group.refresh_from_db()
        criteria = check_certification_criteria(group)
        self.assertTrue(criteria["creation"])

    def test_supportgroup_members(self):
        group = SupportGroup.objects.create(name="G")
        criteria = check_certification_criteria(group)
        self.assertFalse(criteria["members"])

        for i in (1, 2, 3):
            person = Person.objects.create_person(f"m{i}@agir.local", create_role=True)
            Membership.objects.create(
                supportgroup=group,
                person=person,
                membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
            )
            criteria = check_certification_criteria(group)
            self.assertEqual(criteria["members"], i == 3)

    def test_supportgroup_activity(self):
        group = SupportGroup.objects.create(name="G", location_country="UK")
        criteria = check_certification_criteria(group)
        self.assertNotIn("activity", criteria)
        group.location_country = "FR"
        group.save()
        group.refresh_from_db()
        criteria = check_certification_criteria(group)
        self.assertFalse(criteria["activity"])

        too_old_event = Event.objects.create(
            name="Evenement test",
            visibility=Event.VISIBILITY_PUBLIC,
            start_time=timezone.now() - timedelta(days=93),
            end_time=timezone.now() - timedelta(days=93) + timedelta(minutes=30),
        )
        OrganizerConfig.objects.create(
            event=too_old_event, person=self.person, as_group=group, is_creator=True
        )
        criteria = check_certification_criteria(group)
        self.assertFalse(criteria["activity"])

        for i in (1, 2, 3):
            start = timezone.now() - timedelta(days=62) + timedelta(days=i)
            event = Event.objects.create(
                name="Evenement test",
                visibility=Event.VISIBILITY_PUBLIC,
                start_time=start,
                end_time=start + timedelta(minutes=30),
            )
            OrganizerConfig.objects.create(
                event=event, person=self.person, as_group=group, is_creator=True
            )
            criteria = check_certification_criteria(group)
            self.assertEqual(criteria["activity"], i == 3)

    def test_supportgroup_gender(self):
        group = SupportGroup.objects.create(name="G")
        criteria = check_certification_criteria(group)
        self.assertFalse(criteria["gender"])

        person = Person.objects.create_person(
            f"f@agir.local", gender=Person.GENDER_FEMALE, create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = check_certification_criteria(group)
        self.assertFalse(criteria["gender"])

        person = Person.objects.create_person(
            f"ff@agir.local", gender=Person.GENDER_FEMALE, create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = check_certification_criteria(group)
        self.assertFalse(criteria["gender"])

        person = Person.objects.create_person(
            f"m@agir.local", gender=Person.GENDER_MALE, create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )
        criteria = check_certification_criteria(group)
        self.assertFalse(criteria["gender"])

        person = Person.objects.create_person(
            f"mm@agir.local", gender=Person.GENDER_MALE, create_role=True
        )
        Membership.objects.create(
            supportgroup=group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = check_certification_criteria(group)
        self.assertTrue(criteria["gender"])

    def test_supportgroup_exclusivity(self):
        local_subtype = SupportGroupSubtype.objects.create(
            type=SupportGroup.TYPE_LOCAL_GROUP, label="local"
        )
        local_group = SupportGroup.objects.create(name="G")
        local_group.subtypes.add(local_subtype)

        criteria = check_certification_criteria(local_group)
        self.assertTrue(criteria["exclusivity"])

        person = Person.objects.create_person(f"f@agir.local", create_role=True)
        Membership.objects.create(
            supportgroup=local_group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = check_certification_criteria(local_group)
        self.assertTrue(criteria["exclusivity"])

        pro_subtype = SupportGroupSubtype.objects.create(
            type=SupportGroup.TYPE_LOCAL_GROUP, label="pro"
        )
        second_group = SupportGroup.objects.create(name="GG")
        second_group.subtypes.add(pro_subtype)
        Membership.objects.create(
            supportgroup=second_group,
            person=person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        criteria = check_certification_criteria(local_group)
        self.assertTrue(criteria["exclusivity"])

        second_group.type = SupportGroup.TYPE_LOCAL_GROUP
        second_group.save()
        criteria = check_certification_criteria(local_group)
        self.assertTrue(criteria["exclusivity"])

        second_group.certification_date = timezone.now()
        second_group.save()
        second_group.refresh_from_db()
        self.assertTrue(second_group.is_certified)
        criteria = check_certification_criteria(local_group)
        self.assertTrue(criteria["exclusivity"])

        second_group.subtypes.add(local_subtype)
        criteria = check_certification_criteria(local_group)
        self.assertFalse(criteria["exclusivity"])
