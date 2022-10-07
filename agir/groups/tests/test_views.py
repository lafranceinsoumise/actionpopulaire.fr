import re
from unittest import mock
from unittest.mock import patch

from django.core import mail
from django.test import TestCase
from django.utils import timezone
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.reverse import reverse

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.events.models import Event, OrganizerConfig
from agir.groups.tasks import invite_to_group
from agir.people.models import Person
from ..forms import SupportGroupForm
from ..models import SupportGroup, Membership, SupportGroupSubtype
from ...activity.models import Activity

from agir.lib.tests.mixins import create_group


class SupportGroupMixin:
    def setUp(self):
        self.person = Person.objects.create_insoumise("test@test.com", create_role=True)
        self.other_person = Person.objects.create_insoumise(
            "other@test.fr", create_role=True
        )

        self.referent_group = SupportGroup.objects.create(name="Referent")
        Membership.objects.create(
            person=self.person,
            supportgroup=self.referent_group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

        self.manager_group = SupportGroup.objects.create(
            name="Manager",
            location_name="location",
            location_address1="somewhere",
            location_city="Over",
            location_country="DE",
        )

        Membership.objects.create(
            person=self.person,
            supportgroup=self.manager_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )

        self.member_group = SupportGroup.objects.create(name="Member")
        Membership.objects.create(
            person=self.person,
            supportgroup=self.member_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        # other memberships
        Membership.objects.create(
            person=self.other_person,
            supportgroup=self.member_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.event = Event.objects.create(
            name="événement test pour groupe",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

        OrganizerConfig.objects.create(
            event=self.event, person=self.person, as_group=self.referent_group
        )

        self.client.force_login(self.person.role)


class SupportGroupPageTestCase(SupportGroupMixin, TestCase):
    def test_basic_membr_can_quit_group(self):
        response = self.client.get(
            reverse("quit_group", kwargs={"pk": self.member_group.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("quit_group", kwargs={"pk": self.member_group.pk})
        )
        self.assertRedirects(response, reverse("dashboard"))

        self.assertFalse(
            self.member_group.memberships.filter(person=self.person).exists()
        )

    @mock.patch("agir.groups.views.public_views.someone_joined_notification")
    def test_can_join(self, someone_joined):
        url = reverse("view_group", kwargs={"pk": self.manager_group.pk})
        self.client.force_login(self.other_person.role)
        response = self.client.get(url)
        self.assertNotIn(self.other_person, self.manager_group.members.all())

        response = self.client.post(url, data={"action": "join"}, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.other_person, self.manager_group.members.all())

        someone_joined.assert_called_once()
        membership = Membership.objects.get(
            person=self.other_person, supportgroup=self.manager_group
        )
        self.assertEqual(someone_joined.call_args[0][0], membership)


class ManageSupportGroupTestCase(SupportGroupMixin, TestCase):
    @mock.patch.object(SupportGroupForm, "geocoding_task")
    @mock.patch("agir.groups.forms.send_support_group_creation_notification")
    def test_can_create_group(
        self,
        patched_send_support_group_creation_notification,
        patched_geocode_support_group,
    ):
        self.client.force_login(self.person.role)

        # get create page
        response = self.client.get(reverse("create_group"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("perform_create_group"),
            data={
                "name": "New name",
                "type": "L",
                "subtypes": ["groupe local"],
                "contact_email": "a@fhezfe.fr",
                "contact_phone": "+33606060606",
                "contact_hide_phone": "on",
                "location_name": "location",
                "location_address1": "somewhere",
                "location_city": "Over",
                "location_country": "DE",
                "notify": "on",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        try:
            membership = (
                self.person.memberships.filter(
                    membership_type=Membership.MEMBERSHIP_TYPE_REFERENT
                )
                .exclude(supportgroup=self.referent_group)
                .get()
            )
        except (Membership.DoesNotExist, Membership.MultipleObjectsReturned):
            self.fail("Should have created one membership")

        patched_send_support_group_creation_notification.delay.assert_called_once()
        self.assertEqual(
            patched_send_support_group_creation_notification.delay.call_args[0],
            (membership.pk,),
        )

        patched_geocode_support_group.delay.assert_called_once()
        self.assertEqual(
            patched_geocode_support_group.delay.call_args[0],
            (membership.supportgroup.pk,),
        )

        group = SupportGroup.objects.first()
        self.assertEqual(group.name, "New name")
        self.assertEqual(group.subtypes.all().count(), 1)

    @mock.patch("agir.lib.tasks.geocode_person")
    def test_cannot_view_unpublished_group(self, geocode_person):
        self.client.force_login(self.person.role)

        self.referent_group.published = False
        self.referent_group.save()

        res = self.client.get("/groupes/{}/".format(self.referent_group.pk))
        self.assertEqual(res.status_code, status.HTTP_410_GONE)

        group_pages = [
            "change_group_location",
            "quit_group",
        ]
        for page in group_pages:
            res = self.client.get(reverse(page, args=(self.referent_group.pk,)))
            self.assertEqual(
                res.status_code,
                status.HTTP_404_NOT_FOUND,
                '"{}" did not return 404'.format(page),
            )

    def test_transfer_allowed_for_managers(self):
        res = self.client.post(
            reverse("transfer_group_members", kwargs={"pk": self.manager_group.pk})
        )
        self.assertNotEqual(res.status_code, 403)


class InvitationTestCase(TestCase):
    def setUp(self) -> None:
        self.group = SupportGroup.objects.create(name="Nom du groupe")
        self.referent = Person.objects.create_insoumise(
            "user@example.com", create_role=True
        )

        Membership.objects.create(
            supportgroup=self.group,
            person=self.referent,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

        self.invitee = Person.objects.create_insoumise("user2@example.com")

    def test_activity_is_created_for_existing_user(self):
        invite_to_group(self.group.pk, "user2@example.com", self.referent.pk)

        self.assertEqual(len(mail.outbox), 0)

        activities = Activity.objects.filter(recipient=self.invitee)
        self.assertEqual(activities.count(), 1)

        activity = activities.get()

        self.assertEqual(activity.type, Activity.TYPE_GROUP_INVITATION)
        self.assertEqual(activity.supportgroup, self.group)

    def test_invitation_mail_is_sent_to_new_user(self):
        invite_to_group(self.group.pk, "userunknown@example.com", self.referent.pk)

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(
            email.subject, "Vous avez été invité⋅e à rejoindre la France insoumise"
        )

        self.assertIn(
            "Vous avez été invité⋅e à rejoindre la France insoumise et le groupe d'action « Nom du groupe » par un de ses animateurs",
            email.body,
        )

        self.assertIn("groupes/inscription/?", email.body)

        join_url = re.search(
            "/groupes/inscription/\?[%.A-Za-z0-9&=_-]+", email.body
        ).group(0)

        res = self.client.get(join_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Vous avez été invité⋅e à rejoindre")

        res = self.client.post(
            join_url,
            data={
                "location_zip": "33000",
                "subscribed": "Y",
                "join_support_group": "Y",
            },
        )

        self.assertEqual(res.status_code, 200)
        self.assertContains(
            res,
            "Vous venez de rejoindre la France insoumise. Nous en sommes très heureux.",
        )

        self.assertTrue(
            Person.objects.filter(emails__address="userunknown@example.com").exists()
        )

        self.assertTrue(
            Membership.objects.filter(
                person__emails__address="userunknown@example.com",
                supportgroup=self.group,
            )
        )

    @patch("agir.groups.views.management_views.send_abuse_report_message")
    def test_can_report_abuse_when_not_subscribed(self, send_abuse_report_message):
        email_address = "userunknown@example.com"
        invite_to_group(self.group.pk, email_address, self.referent.pk)
        email = mail.outbox[-1]

        self.assertIn("/groupes/invitation/abus/", email.body)

        report_url = re.search(
            r"/groupes/invitation/abus/\?[%.A-za-z0-9&=-]+", email.body
        ).group(0)

        # following to make it work with auto_login
        res = self.client.get(report_url, follow=True)
        self.assertContains(res, "Signaler un email non sollicité")
        self.assertContains(res, "<form")

        if res.redirect_chain:
            res = self.client.post(res.redirect_chain[-1][0])
        else:
            res = self.client.post(report_url)

        self.assertContains(res, "Merci de votre signalement")

        send_abuse_report_message.delay.assert_called_once()
        self.assertEqual(
            send_abuse_report_message.delay.call_args[0], (str(self.referent.id),)
        )


class GroupDetailAPIViewTestCase(TestCase):
    def test_published_groups_are_accessible(self):
        active_group = SupportGroup.objects.create(name="Active Group", published=True)
        self.assertEqual(active_group.published, True)
        response = self.client.get(
            reverse("api_group_view", kwargs={"pk": active_group.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unpublished_groups_are_not_accessible(self):
        inactive_group = SupportGroup.objects.create(
            name="Active Group", published=False
        )
        self.assertEqual(inactive_group.published, False)
        response = self.client.get(
            reverse("api_group_view", kwargs={"pk": inactive_group.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GroupAPIUpcomingEventViewTestCase(SupportGroupMixin, TestCase):
    def test_upcoming_is_empty_when_no_events(self):
        self.inactive_group = SupportGroup.objects.create(
            name="Manager",
            location_name="location",
            location_address1="somewhere",
            location_city="Over",
            location_country="DE",
        )
        response = self.client.get(
            reverse("api_group_upcoming_events_view", kwargs={"pk": self.inactive_group.pk})
        )

        self.assertFalse(self.manager_group.organized_events.upcoming().exists())
        self.assertEqual(response.data, [])

    def test_upcoming_is_empty_when_only_past_events_exists(self):
        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.event = Event.objects.create(
            name="événement terminé pour test",
            start_time=now - 3 * day,
            end_time=now - 3 * day + 4 * hour,
        )

        OrganizerConfig.objects.create(
            event=self.event, person=self.person, as_group=self.manager_group
        )

        response = self.client.get(
            reverse("api_group_upcoming_events_view", kwargs={"pk": self.manager_group.pk})
        )

        self.assertFalse(self.manager_group.organized_events.upcoming().exists())
        self.assertEqual(len(response.data), 0)

    def test_upcoming_contains_only_upcoming_events(self):
        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.event = Event.objects.create(
            name="événement dans le futur pour test",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

        self.past_event = Event.objects.create(
            name="événement dans le passé pour test",
            start_time=now - 3 * day,
            end_time=now - 3 * day + 4 * hour,
        )

        OrganizerConfig.objects.create(
            event=self.event, person=self.person, as_group=self.manager_group
        )

        OrganizerConfig.objects.create(
            event=self.past_event, person=self.person, as_group=self.manager_group
        )

        response = self.client.get(
            reverse("api_group_upcoming_events_view", kwargs={"pk": self.manager_group.pk})
        )

        # upcoming events size must be 1
        self.assertEqual(self.manager_group.organized_events.upcoming().count(), 1)
        self.assertEqual(len(response.data), 1)
