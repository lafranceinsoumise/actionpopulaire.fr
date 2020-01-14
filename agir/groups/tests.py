from unittest import mock
from unittest.mock import patch

import re
from django.contrib.messages import get_messages
from django.core import mail
from django.db import IntegrityError
from django.shortcuts import reverse as dj_reverse
from django.test import TestCase
from django.utils import timezone
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.events.models import Event, OrganizerConfig
from agir.groups.tasks import send_someone_joined_notification, invite_to_group
from agir.lib.tests.mixins import FakeDataMixin
from agir.people.models import Person
from . import tasks
from .forms import SupportGroupForm
from .models import SupportGroup, Membership, SupportGroupSubtype


class BasicSupportGroupTestCase(TestCase):
    def test_can_create_supportgroup(self):
        group = SupportGroup.objects.create(name="Groupe d'action")


class MembershipTestCase(APITestCase):
    def setUp(self):
        self.supportgroup = SupportGroup.objects.create(name="Test")

        self.person = Person.objects.create(email="marc.machin@truc.com")

        self.privileged_user = Person.objects.create_superperson("super@user.fr", None)

    def test_can_create_membership(self):
        Membership.objects.create(supportgroup=self.supportgroup, person=self.person)

    def test_cannot_create_without_person(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(supportgroup=self.supportgroup)

    def test_cannot_create_without_supportgroup(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(person=self.person)

    def test_unique_membership(self):
        Membership.objects.create(person=self.person, supportgroup=self.supportgroup)

        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person, supportgroup=self.supportgroup
            )

    @mock.patch("agir.groups.tasks.send_mosaico_email")
    def test_someone_joined_notification(self, send_mosaico_email):
        Membership.objects.create(
            person=self.privileged_user, supportgroup=self.supportgroup, is_manager=True
        )
        new_membership = Membership.objects.create(
            person=self.person, supportgroup=self.supportgroup
        )
        send_someone_joined_notification(new_membership.pk)

        send_mosaico_email.assert_called_once()
        self.assertEqual(
            send_mosaico_email.call_args[1]["recipients"], [self.privileged_user]
        )


class EventTasksTestCase(TestCase):
    def setUp(self):
        now = timezone.now()

        self.creator = Person.objects.create_person("moi@moi.fr")
        self.group = SupportGroup.objects.create(
            name="Mon événement",
            contact_name="Moi",
            contact_email="monevenement@moi.fr",
            contact_phone="06 06 06 06 06",
            contact_hide_phone=False,
            location_name="ma maison",
            location_address1="Place denfert-rochereau",
            location_zip="75014",
            location_city="Paris",
            location_country="FR",
        )

        self.creator_membership = Membership.objects.create(
            person=self.creator,
            supportgroup=self.group,
            is_referent=True,
            is_manager=True,
        )

        self.member1 = Person.objects.create_person("person1@participants.fr")
        self.member2 = Person.objects.create_person("person2@participants.fr")
        self.member_no_notification = Person.objects.create_person(
            "person3@participants.fr"
        )

        self.membership1 = Membership.objects.create(
            supportgroup=self.group, person=self.member1
        )
        self.membership2 = Membership.objects.create(
            supportgroup=self.group, person=self.member2
        )
        self.membership3 = Membership.objects.create(
            supportgroup=self.group,
            person=self.member_no_notification,
            notifications_enabled=False,
        )

    def test_group_creation_mail(self):
        tasks.send_support_group_creation_notification(self.creator_membership.pk)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.recipients(), ["moi@moi.fr"])

        text = message.body.replace("\n", "")

        for item in [
            "name",
            "location_name",
            "short_address",
            "contact_name",
            "contact_phone",
        ]:
            self.assert_(
                getattr(self.group, item) in text, "{} missing in message".format(item)
            )

    def test_someone_joined_notification_mail(self):
        tasks.send_someone_joined_notification(self.membership1.pk)

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.recipients(), ["moi@moi.fr"])

        text = message.body.replace("\n", "")

        mail_content = {
            "member information": str(self.member1),
            "group name": self.group.name,
            "group management link": dj_reverse(
                "manage_group",
                kwargs={"pk": self.group.pk},
                urlconf="agir.api.front_urls",
            ),
        }

        for name, value in mail_content.items():
            self.assert_(value in text, "{} missing from mail".format(name))

    def test_changed_group_notification_mail(self):
        tasks.send_support_group_changed_notification(
            self.group.pk, ["information", "contact"]
        )

        self.assertEqual(len(mail.outbox), 3)

        for message in mail.outbox:
            self.assertEqual(len(message.recipients()), 1)

        messages = {message.recipients()[0]: message for message in mail.outbox}

        self.assertCountEqual(
            messages.keys(),
            [self.creator.email, self.member1.email, self.member2.email],
        )

        for recipient, message in messages.items():
            text = message.body.replace("\n", "")

            self.assert_(self.group.name in text, "group name not in message")
            # self.assert_(
            #     dj_reverse('quit_group', kwargs={'pk': self.group.pk}, urlconf='front.urls') in message.body,
            #     'quit group link not in message'
            # )
            self.assertIn(
                "/groupes/{}".format(self.group.pk), text, "group link not in message"
            )

            self.assertIn(str(tasks.CHANGE_DESCRIPTION["information"]), text)
            self.assertIn(str(tasks.CHANGE_DESCRIPTION["contact"]), text)
            self.assertNotIn(str(tasks.CHANGE_DESCRIPTION["location"]), text)


class GroupSubtypesTestCase(FakeDataMixin, TestCase):
    def test_local_groups_have_subtype(self):
        self.data["groups"]["user1_group"].subtypes.add(
            SupportGroupSubtype.objects.get(label="groupe local")
        )


class GroupPageTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("test@test.com")
        self.other_person = Person.objects.create_person("other@test.fr")

        self.referent_group = SupportGroup.objects.create(name="Referent")
        Membership.objects.create(
            person=self.person, supportgroup=self.referent_group, is_referent=True
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
            is_referent=False,
            is_manager=True,
        )

        self.member_group = SupportGroup.objects.create(name="Member")
        Membership.objects.create(person=self.person, supportgroup=self.member_group)

        # other memberships
        Membership.objects.create(
            person=self.other_person, supportgroup=self.member_group
        )

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.event = Event.objects.create(
            name="événement test pour groupe",
            nb_path="/pseudo/test",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

        OrganizerConfig.objects.create(
            event=self.event, person=self.person, as_group=self.referent_group
        )

        self.client.force_login(self.person.role)

    @mock.patch.object(SupportGroupForm, "geocoding_task")
    @mock.patch("agir.groups.forms.send_support_group_changed_notification")
    def test_can_modify_managed_group(self, patched_send_notification, patched_geocode):
        response = self.client.get(
            reverse("edit_group", kwargs={"pk": self.manager_group.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("edit_group", kwargs={"pk": self.manager_group.pk}),
            data={
                "name": "Manager",
                "type": "L",
                "subtypes": ["groupe local"],
                "contact_name": "Arthur",
                "contact_email": "a@fhezfe.fr",
                "contact_phone": "06 06 06 06 06",
                "location_name": "location",
                "location_address1": "somewhere",
                "location_city": "Outside",
                "location_country": "DE",
                "notify": "on",
            },
        )

        self.assertRedirects(
            response, reverse("manage_group", kwargs={"pk": self.manager_group.pk})
        )

        # accessing the messages: see https://stackoverflow.com/a/14909727/1122474
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level_tag, "success")

        # send_support_group_changed_notification.delay should have been called once, with the pk of the group as
        # first argument, and the changes as the second
        patched_send_notification.delay.assert_called_once()
        args = patched_send_notification.delay.call_args[0]

        self.assertEqual(args[0], self.manager_group.pk)
        self.assertCountEqual(args[1], ["contact", "location"])

        patched_geocode.delay.assert_called_once()
        args = patched_geocode.delay.call_args[0]

        self.assertEqual(args[0], self.manager_group.pk)

    @mock.patch("agir.groups.forms.geocode_support_group")
    def test_do_not_geocode_if_address_did_not_change(self, patched_geocode):
        response = self.client.post(
            reverse("edit_group", kwargs={"pk": self.manager_group.pk}),
            data={
                "name": "Manager",
                "type": "L",
                "subtypes": ["groupe local"],
                "location_name": "location",
                "location_address1": "somewhere",
                "location_city": "Over",
                "location_country": "DE",
                "contact_name": "Arthur",
                "contact_email": "a@fhezfe.fr",
                "contact_phone": "06 06 06 06 06",
            },
        )

        self.assertRedirects(
            response, reverse("manage_group", kwargs={"pk": self.manager_group.pk})
        )
        patched_geocode.delay.assert_not_called()

    def test_cannot_modify_member_group(self):
        response = self.client.get(
            reverse("edit_group", kwargs={"pk": self.member_group.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch("agir.people.views.dashboard.geocode_person")
    def test_can_quit_group(self, geocode_person):
        response = self.client.get(
            reverse("quit_group", kwargs={"pk": self.member_group.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("quit_group", kwargs={"pk": self.member_group.pk})
        )
        self.assertRedirects(response, reverse("dashboard"))
        geocode_person.delay.assert_called_once()

        self.assertFalse(
            self.member_group.memberships.filter(person=self.person).exists()
        )

    @mock.patch("agir.groups.views.public_views.send_someone_joined_notification")
    def test_can_join(self, someone_joined):
        url = reverse("view_group", kwargs={"pk": self.manager_group.pk})
        self.client.force_login(self.other_person.role)
        response = self.client.get(url)
        self.assertNotIn(self.other_person, self.manager_group.members.all())
        self.assertIn("Rejoindre ce groupe", response.content.decode())

        response = self.client.post(url, data={"action": "join"}, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.other_person, self.manager_group.members.all())
        self.assertIn("Quitter le groupe", response.content.decode())

        someone_joined.delay.assert_called_once()
        membership = Membership.objects.get(
            person=self.other_person, supportgroup=self.manager_group
        )
        self.assertEqual(someone_joined.delay.call_args[0][0], membership.pk)

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
                self.person.memberships.filter(is_referent=True)
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

    @mock.patch("agir.people.views.dashboard.geocode_person")
    def test_cannot_view_unpublished_group(self, geocode_person):
        self.client.force_login(self.person.role)

        self.referent_group.published = False
        self.referent_group.save()

        res = self.client.get(reverse("dashboard"))
        self.assertNotContains(res, self.referent_group.pk)
        geocode_person.delay.assert_called_once()

        res = self.client.get("/groupes/{}/".format(self.referent_group.pk))
        self.assertEqual(res.status_code, status.HTTP_410_GONE)

        group_pages = [
            "manage_group",
            "edit_group",
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

    def test_can_see_groups_events(self):
        response = self.client.get(reverse("view_group", args=[self.referent_group.pk]))

        self.assertContains(response, "événement test pour groupe")

    def test_cannot_join_group_if_external(self):
        self.other_person.is_insoumise = False
        self.other_person.save()
        self.client.force_login(self.other_person.role)

        # cannot see button
        url = reverse("view_group", kwargs={"pk": self.manager_group.pk})
        response = self.client.get(url)
        self.assertNotIn("Rejoindre ce groupe", response.content.decode())
        self.assertIn("Groupe réservé aux insoumis⋅es", response.content.decode())

        # cannot join
        self.client.post(url, data={"action": "join"}, follow=True)
        self.assertNotIn(self.other_person, self.manager_group.members.all())


class ExternalJoinSupportGroupTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("test@test.com", is_insoumise=False)
        self.subtype = SupportGroupSubtype.objects.create(
            type=SupportGroup.TYPE_LOCAL_GROUP, allow_external=True
        )
        self.group = SupportGroup.objects.create(name="Simple Event")
        self.group.subtypes.add(self.subtype)

    def test_cannot_external_join_if_does_not_allow_external(self):
        self.subtype.allow_external = False
        self.subtype.save()
        subscription_token = subscription_confirmation_token_generator.make_token(
            email="test1@test.com"
        )
        query_args = {"email": "test1@test.com", "token": subscription_token}
        self.client.get(
            reverse("external_join_group", args=[self.group.pk])
            + "?"
            + urlencode(query_args)
        )

        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(email="test1@test.com")

    def test_can_join(self):
        res = self.client.get(reverse("view_group", args=[self.group.pk]))
        self.assertNotContains(res, "Se connecter pour")
        self.assertContains(res, "Rejoindre ce groupe")

        self.client.post(
            reverse("external_join_group", args=[self.group.pk]),
            data={"email": self.person.email},
        )
        self.assertEqual(self.person.rsvps.all().count(), 0)

        subscription_token = subscription_confirmation_token_generator.make_token(
            email=self.person.email
        )
        query_args = {"email": self.person.email, "token": subscription_token}
        self.client.get(
            reverse("external_join_group", args=[self.group.pk])
            + "?"
            + urlencode(query_args)
        )

        self.assertEqual(self.person.supportgroups.first(), self.group)

    def test_can_rsvp_without_account(self):
        self.client.post(
            reverse("external_join_group", args=[self.group.pk]),
            data={"email": "test1@test.com"},
        )

        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(email="test1@test.com")

        subscription_token = subscription_confirmation_token_generator.make_token(
            email="test1@test.com"
        )
        query_args = {"email": "test1@test.com", "token": subscription_token}
        self.client.get(
            reverse("external_join_group", args=[self.group.pk])
            + "?"
            + urlencode(query_args)
        )

        self.assertEqual(
            Person.objects.get(email="test1@test.com").supportgroups.first(), self.group
        )
        self.assertEqual(Person.objects.get(email="test1@test.com").is_insoumise, False)


class InvitationTestCase(TestCase):
    def setUp(self) -> None:
        self.group = SupportGroup.objects.create(name="Nom du groupe")
        self.referent = Person.objects.create_person("user@example.com")

        Membership.objects.create(
            supportgroup=self.group,
            person=self.referent,
            is_referent=True,
            is_manager=True,
        )

        self.invitee = Person.objects.create_person("user2@example.com")

    @patch("agir.groups.forms.invite_to_group")
    def test_can_invite_already_subscribed_person(self, invite_to_group):
        self.client.force_login(self.referent.role)
        res = self.client.get(reverse("manage_group", args=(self.group.pk,)))

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "invitation_form")

        res = self.client.post(
            reverse("manage_group", args=(self.group.pk,)),
            data={"form": "invitation_form", "email": "user2@example.com"},
        )

        self.assertRedirects(res, reverse("manage_group", args=(self.group.pk,)))

        invite_to_group.delay.assert_called_once()
        self.assertEqual(
            invite_to_group.delay.call_args[0],
            (str(self.group.pk), "user2@example.com", str(self.referent.pk)),
        )

    @patch("agir.groups.forms.invite_to_group")
    def test_can_invite_unsubscribed(self, invite_to_group):
        self.client.force_login(self.referent.role)
        res = self.client.get(reverse("manage_group", args=(self.group.pk,)))

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "invitation_form")

        res = self.client.post(
            reverse("manage_group", args=(self.group.pk,)),
            data={"form": "invitation_form", "email": "userunknown@example.com"},
        )

        self.assertRedirects(res, reverse("manage_group", args=(self.group.pk,)))

        invite_to_group.delay.assert_called_once()
        self.assertEqual(
            invite_to_group.delay.call_args[0],
            (str(self.group.pk), "userunknown@example.com", str(self.referent.pk)),
        )

    def test_invitation_mail_is_sent_to_existing_user(self):
        invite_to_group(self.group.pk, "user2@example.com", self.referent.pk)

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(
            email.subject, "Vous avez été invité à rejoindre un groupe de la FI"
        )

        self.assertIn(
            "Vous avez été invité à rejoindre le groupe d'action « Nom du groupe » par un de ses animateurs",
            email.body,
        )

        self.assertIn("/groupes/invitation/?", email.body)

        join_url = re.search(
            "/groupes/invitation/\?[A-Za-z0-9&=_-]+", email.body
        ).group(0)

        res = self.client.get(join_url, follow=True)

        self.assertRedirects(
            res,
            reverse("view_group", args=(self.group.pk,)),
            fetch_redirect_response=False,
        )

        self.assertTrue(
            any(
                "Vous venez de rejoindre le groupe d'action <em>Nom du groupe</em>"
                in m.message
                for m in get_messages(res.wsgi_request)
            )
        )

        self.assertTrue(
            Membership.objects.filter(
                person=self.invitee, supportgroup=self.group
            ).exists()
        )

    def test_invitation_mail_is_sent_to_new_user(self):
        invite_to_group(self.group.pk, "userunknown@example.com", self.referent.pk)

        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]

        self.assertEqual(
            email.subject, "Vous avez été invité à rejoindre la France insoumise"
        )

        self.assertIn(
            "Vous avez été invité à rejoindre la France insoumise et le groupe d'action « Nom du groupe » par un de ses animateurs",
            email.body,
        )

        self.assertIn("groupes/inscription/?", email.body)

        join_url = re.search(
            "/groupes/inscription/\?[%.A-Za-z0-9&=_-]+", email.body
        ).group(0)

        res = self.client.get(join_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(
            res, "<h2>Vous avez été invité à rejoindre la France insoumise</h2>"
        )

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
    def test_can_report_abuse_from_both_emails(self, send_abuse_report_message):
        call_count = 0

        for email_address in ["user2@example.com", "userunknown@example.com"]:
            invite_to_group(self.group.pk, email_address, self.referent.pk)
            email = mail.outbox[-1]

            self.assertIn("/groupes/invitation/abus/", email.body)

            report_url = re.search(
                r"/groupes/invitation/abus/\?[%.A-za-z0-9&=-]+", email.body
            ).group(0)

            # following to make it work with auto_login
            res = self.client.get(report_url, follow=True)
            self.assertContains(res, "<h2>Signaler un email non sollicité</h2>")
            self.assertContains(res, "<form")

            if res.redirect_chain:
                res = self.client.post(res.redirect_chain[-1][0])
            else:
                res = self.client.post(report_url)

            self.assertContains(res, "<h2>Merci de votre signalement</h2>")

            call_count += 1
            self.assertEqual(send_abuse_report_message.delay.call_count, call_count)
            self.assertEqual(
                send_abuse_report_message.delay.call_args[0], (str(self.referent.id),)
            )
