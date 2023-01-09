from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from agir.events.models import Event, OrganizerConfig
from agir.people.models import Person
from ..models import SupportGroup, Membership
from ..utils import (
    DAYS_SINCE_LAST_EVENT_WARNING,
    get_soon_to_be_inactive_groups,
    DAYS_SINCE_GROUP_CREATION_LIMIT,
    DAYS_SINCE_LAST_EVENT_LIMIT,
    is_active_group_filter,
)


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


class SoonToBeInactiveSupportGroupQuerysetTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "person@agir.test", create_role=True
        )
        self.client.force_login(self.person.role)
        self.now = timezone.now()
        self.exact_limit_date = self.now - timedelta(days=DAYS_SINCE_LAST_EVENT_WARNING)
        self.older_than_limit_date = self.exact_limit_date - timedelta(days=10)

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

    def assert_group_in_queryset(self, group, exact=False):
        group_pks = list(
            get_soon_to_be_inactive_groups(exact=exact).values_list("pk", flat=True)
        )
        self.assertIn(group.pk, group_pks)

    def assert_group_not_in_queryset(self, group, exact=False):
        group_pks = list(
            get_soon_to_be_inactive_groups(exact=exact).values_list("pk", flat=True)
        )
        self.assertNotIn(group.pk, group_pks)

    def test_new_group_not_in_queryset(self):
        new_group = self.create_group(name="New group")
        self.create_group_event(group=new_group, start_time=self.exact_limit_date)
        self.assert_group_not_in_queryset(new_group)

    def test_active_group_not_in_queryset(self):
        active_group = self.create_group(name="Active group", is_new=False)
        self.create_group_event(group=active_group, start_time=self.exact_limit_date)
        self.create_group_event(group=active_group, start_time=self.now)
        self.assert_group_not_in_queryset(active_group)

    def test_inactive_group_not_in_exact_queryset(self):
        inactive_group = self.create_group(name="Inactive group", is_new=False)
        self.assert_group_not_in_queryset(inactive_group, exact=True)
        self.create_group_event(
            group=inactive_group, start_time=self.older_than_limit_date
        )
        self.assert_group_not_in_queryset(inactive_group, exact=True)

    def test_inactive_group_in_non_exact_queryset(self):
        inactive_group = self.create_group(name="Inactive group", is_new=False)
        self.assert_group_not_in_queryset(inactive_group)
        self.create_group_event(group=inactive_group, start_time=self.exact_limit_date)
        self.assert_group_in_queryset(inactive_group)

    def test_inactive_group_in_exact_queryset(self):
        inactive_group = self.create_group(name="Inactive group", is_new=False)
        self.create_group_event(group=inactive_group, start_time=self.exact_limit_date)
        self.assert_group_in_queryset(inactive_group, exact=True)
