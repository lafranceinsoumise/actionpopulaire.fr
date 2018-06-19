from django.test import TestCase
from django.urls import reverse

from agir.lib.tests.mixins import FakeDataMixin


class CarteTestCase(FakeDataMixin, TestCase):
    def test_can_see_maps_views(self):
        for view_name in ['event_list', 'group_list', 'events_map', 'groups_map']:
            res = self.client.get(reverse('carte:' + view_name))
            self.assertEqual(res.status_code, 200, f"cannot get '{view_name}'")

    def test_can_see_individual_maps(self):
        res = self.client.get(reverse('carte:single_event_map', args=[self.events['user1_event1'].pk]))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('carte:single_group_map', args=[self.groups['user1_group'].pk]))
        self.assertEqual(res.status_code, 200)
