from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

# Create your tests here.
from nuntius.models import Campaign

from agir.mailing.models import Segment
from agir.people.models import Person


class SegmentTestCase(TestCase):
    def setUp(self) -> None:
        self.person_with_account = Person.objects.create_insoumise(
            email="a@a.a",
            create_role=True,
        )

        self.person_without_account = Person.objects.create_person(email="b@b.b")

    def test_default_segment_include_anyone(self):
        s = Segment.objects.create(newsletters=[], is_2022=None)

        self.assertIn(self.person_with_account, s.get_subscribers_queryset())
        self.assertIn(self.person_without_account, s.get_subscribers_queryset())

    def test_person_with_disabled_account_not_in_segment(self):
        s = Segment.objects.create(newsletters=[], is_2022=None)
        role = self.person_with_account.role
        role.is_active = False
        role.save()

        self.assertNotIn(self.person_with_account, s.get_subscribers_queryset())

    def test_segment_with_registration_duration(self):
        old_person = Person.objects.create_person(
            email="old@agir.local", created=now() - timedelta(hours=2)
        )
        new_person = Person.objects.create_person(email="new@agir.local", created=now())
        s = Segment.objects.create(
            newsletters=[], is_2022=None, registration_duration=1
        )
        self.assertIn(old_person, s.get_subscribers_queryset())
        self.assertNotIn(new_person, s.get_subscribers_queryset())


class SendCampaignActionTestCase(TestCase):
    def setUp(self):
        self.admin = Person.objects.create_superperson("admin@agir.test", "password")
        self.user_with_newsletters = Person.objects.create_person(
            "newsletters@agir.test", newsletters=[Person.NEWSLETTER_LFI]
        )
        self.user_without_newsletters = Person.objects.create_person(
            "no_newsletters@agir.test", newsletters=[]
        )
        self.segment_with_newsletters = Segment.objects.create(
            newsletters=[Person.NEWSLETTER_LFI], is_2022=None
        )
        self.segment_without_newsletters = Segment.objects.create(
            newsletters=[], is_2022=None
        )
        self.assertIn(
            self.user_without_newsletters,
            self.segment_without_newsletters.get_subscribers_queryset(),
        )
        self.assertIn(
            self.user_with_newsletters,
            self.segment_with_newsletters.get_subscribers_queryset(),
        )

    def test_no_confirmation_needed_to_send_if_all_subscribers_have_newsletters(self):
        self.client.force_login(
            self.admin.role, backend="agir.people.backend.PersonBackend"
        )
        campaign = Campaign.objects.create(
            name="campaign", segment=self.segment_with_newsletters
        )
        self.assertEqual(campaign.status, Campaign.STATUS_WAITING)
        send_url = reverse("admin:nuntius_campaign_send", args=[campaign.pk])
        res = self.client.get(send_url)
        self.assertEqual(res.status_code, 302)
        campaign.refresh_from_db(fields=("status",))
        self.assertEqual(campaign.status, Campaign.STATUS_SENDING)

    def test_confirmation_needed_to_send_if_some_subscribers_do_not_have_newsletters(
        self,
    ):
        self.client.force_login(
            self.admin.role, backend="agir.people.backend.PersonBackend"
        )
        campaign = Campaign.objects.create(
            name="campaign", segment=self.segment_without_newsletters
        )
        self.assertEqual(campaign.status, Campaign.STATUS_WAITING)
        send_url = reverse("admin:nuntius_campaign_send", args=[campaign.pk])
        res = self.client.get(send_url)
        self.assertEqual(res.status_code, 200, res)
        campaign.refresh_from_db(fields=("status",))
        self.assertEqual(campaign.status, Campaign.STATUS_WAITING)
        self.assertContains(res, '<input type="submit" name="confirmation"')

    def test_can_confirm_sending_campaign_to_subscribers_without_newsletters(self):
        self.client.force_login(
            self.admin.role, backend="agir.people.backend.PersonBackend"
        )
        campaign = Campaign.objects.create(
            name="campaign", segment=self.segment_without_newsletters
        )
        self.assertEqual(campaign.status, Campaign.STATUS_WAITING)
        send_url = reverse("admin:nuntius_campaign_send", args=[campaign.pk])
        res = self.client.post(send_url, {"confirmation": True})
        self.assertEqual(res.status_code, 302, res)
        campaign.refresh_from_db(fields=("status",))
        self.assertEqual(campaign.status, Campaign.STATUS_SENDING)
