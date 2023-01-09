from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

# Create your tests here.
from faker import Faker
from nuntius.models import Campaign

from agir.groups.models import SupportGroupSubtype, SupportGroup, Membership
from agir.mailing.models import Segment
from agir.people.models import Person

fake = Faker("fr_FR")


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


class SegmentSupportgroupFilterTestCase(TestCase):
    def create_group(self, subtype=None, **kwargs):
        if subtype is None:
            subtype = self.default_subtype
        kwargs["name"] = f"Groupe de {fake.city()}"
        group = SupportGroup.objects.create(**kwargs)
        group.subtypes.add(subtype)

        return group

    def create_member(
        self, membership_type=Membership.MEMBERSHIP_TYPE_MEMBER, supportgroup=None
    ):
        if supportgroup is None:
            supportgroup = self.default_group
        member = Person.objects.create_insoumise(
            email=fake.email(),
            create_role=True,
        )
        Membership.objects.create(
            supportgroup=supportgroup, person=member, membership_type=membership_type
        )

        return member

    def create_manager(self, *args, **kwargs):
        return self.create_member(
            *args, membership_type=Membership.MEMBERSHIP_TYPE_MANAGER, **kwargs
        )

    def create_referent(self, *args, **kwargs):
        return self.create_member(
            *args, membership_type=Membership.MEMBERSHIP_TYPE_REFERENT, **kwargs
        )

    def setUp(self):
        self.default_subtype = SupportGroupSubtype.objects.create(label="default")
        self.default_group = self.create_group(subtype=self.default_subtype)

    def test_default_segment_include_anyone(self):
        includes = [
            self.create_member(),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(newsletters=[], is_2022=None)
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())

    def test_supportgroup_status_not_member_filter(self):
        supportgroup = self.create_group()
        includes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        excludes = [
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            self.create_referent(),
            self.create_referent(supportgroup=supportgroup),
        ]
        s = Segment.objects.create(
            newsletters=[],
            is_2022=None,
            supportgroup_status=Segment.GA_STATUS_NOT_MEMBER,
        )
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())

    def test_supportgroup_status_member_filter(self):
        supportgroup = self.create_group()
        includes = [
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            self.create_referent(),
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            is_2022=None,
            supportgroup_status=Segment.GA_STATUS_MEMBER,
        )
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())

    def test_supportgroup_status_manager_filter(self):
        supportgroup = self.create_group()
        includes = [
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            self.create_referent(),
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            is_2022=None,
            supportgroup_status=Segment.GA_STATUS_MANAGER,
        )
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())

    def test_supportgroup_status_referent_filter(self):
        supportgroup = self.create_group()
        includes = [
            self.create_referent(),
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            is_2022=None,
            supportgroup_status=Segment.GA_STATUS_REFERENT,
        )
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())

    def test_supportgroups_filter(self):
        supportgroup = self.create_group()
        includes = [self.create_member(supportgroup=supportgroup)]
        excludes = [
            self.create_member(),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(newsletters=[], is_2022=None)
        s.supportgroups.add(supportgroup)
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())

    def test_supportgroup_status_and_supportgroups_filter_combo(self):
        supportgroup = self.create_group()
        includes = [
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_referent(),
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            is_2022=None,
            supportgroup_status=Segment.GA_STATUS_REFERENT,
        )
        s.supportgroups.add(supportgroup)
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())

    def test_supportgroup_subtypes_filter(self):
        subtype = SupportGroupSubtype.objects.create(label="filtered")
        supportgroup = self.create_group(subtype=subtype)
        includes = [self.create_member(supportgroup=supportgroup)]
        excludes = [
            self.create_member(),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(newsletters=[], is_2022=None)
        s.supportgroup_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())

    def test_supportgroup_status_and_supportgroup_subtypes_filter_combo(self):
        subtype = SupportGroupSubtype.objects.create(label="filtered")
        supportgroup = self.create_group(subtype=subtype)
        includes = [
            self.create_referent(supportgroup=supportgroup),
        ]
        excludes = [
            self.create_referent(),
            self.create_member(),
            self.create_member(supportgroup=supportgroup),
            self.create_manager(),
            self.create_manager(supportgroup=supportgroup),
            Person.objects.create_insoumise(
                email=fake.email(),
                create_role=True,
            ),
        ]
        s = Segment.objects.create(
            newsletters=[],
            is_2022=None,
            supportgroup_status=Segment.GA_STATUS_REFERENT,
        )
        s.supportgroup_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())

    def test_supportgroups_overrides_supportgroup_subtypes_filter(self):
        subtype = SupportGroupSubtype.objects.create(label="filtered")
        subtype_supportgroup = self.create_group(subtype=subtype)
        another_supportgroup = self.create_group()
        includes = [self.create_member(supportgroup=another_supportgroup)]
        excludes = [self.create_member(supportgroup=subtype_supportgroup)]
        s = Segment.objects.create(newsletters=[], is_2022=None)
        s.supportgroups.add(another_supportgroup)
        s.supportgroup_subtypes.add(subtype)
        for person in includes:
            self.assertIn(person, s.get_subscribers_queryset())
        for person in excludes:
            self.assertNotIn(person, s.get_subscribers_queryset())


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
