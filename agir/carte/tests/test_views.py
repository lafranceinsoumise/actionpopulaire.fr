from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from agir.api.redis import using_separate_redis_server
from agir.events.models import Event, EventSubtype
from agir.lib.tests.mixins import FakeDataMixin
from agir.lib.tests.mixins import create_location
from agir.people.models import Person


@using_separate_redis_server
class CarteTestCase(FakeDataMixin, TestCase):
    def test_can_see_maps_views(self):
        for view_name in ["event_list", "group_list", "events_map", "groups_map"]:
            res = self.client.get(reverse("carte:" + view_name))
            self.assertEqual(res.status_code, 200, f"cannot get '{view_name}'")

    def test_can_see_individual_maps(self):
        res = self.client.get(
            reverse("carte:single_event_map", args=[self.events["user1_event1"].pk])
        )
        self.assertEqual(res.status_code, 200)

        res = self.client.get(
            reverse("carte:single_group_map", args=[self.groups["user1_group"].pk])
        )
        self.assertEqual(res.status_code, 200)


@using_separate_redis_server
class EventsMapTestCase(TestCase):
    def setUp(self):
        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.person_insoumise = Person.objects.create_insoumise(
            "person@lfi.com", create_role=True
        )
        self.person_2022 = Person.objects.create_person(
            "person@nsp.com", create_role=True, is_2022=True, is_insoumise=False
        )

        self.subtype = EventSubtype.objects.create(
            label="sous-type",
            visibility=EventSubtype.VISIBILITY_ALL,
            type=EventSubtype.TYPE_PUBLIC_ACTION,
        )
        location = create_location()

        self.event_insoumis = Event.objects.create(
            name="Event Insoumis",
            subtype=self.subtype,
            start_time=now + day,
            end_time=now + day + 4 * hour,
            for_users=Event.FOR_USERS_INSOUMIS,
            **location,
        )
        self.event_2022 = Event.objects.create(
            name="Event NSP",
            subtype=self.subtype,
            start_time=now + day,
            end_time=now + day + 4 * hour,
            for_users=Event.FOR_USERS_2022,
            **location,
        )

    def test_insoumise_persone_can_search_through_all_events(self):
        self.client.force_login(self.person_insoumise.role)
        res = self.client.get(reverse("carte:event_list"))
        self.assertContains(res, self.event_insoumis.name)
        self.assertContains(res, self.event_2022.name)

    def test_2022_only_person_can_search_through_all_events(self):
        self.client.force_login(self.person_2022.role)
        res = self.client.get(reverse("carte:event_list") + "?var=nsp_only")
        self.assertContains(res, self.event_insoumis.name)
        self.assertContains(res, self.event_2022.name)
