import datetime
from datetime import timedelta
from functools import partial
from unittest import mock
from unittest.mock import patch

from django.contrib import messages
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.reverse import reverse

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.carte.views import EventMapView
from agir.events.tasks import (
    send_guest_confirmation,
    send_rsvp_notification,
)
from agir.groups.models import SupportGroup, Membership
from agir.lib.tests.mixins import FakeDataMixin
from agir.lib.utils import front_url
from agir.payments.actions.payments import complete_payment
from agir.payments.models import Payment
from agir.people.models import Person, PersonForm, PersonFormSubmission, PersonTag
from ..models import (
    Event,
    Calendar,
    RSVP,
    OrganizerConfig,
    CalendarItem,
    EventSubtype,
    JitsiMeeting,
    Invitation,
)
from ..views import notification_listener as event_notification_listener


class OrganizerAsGroupTestCase(TestCase):
    def setUp(self):
        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(hours=2)
        self.calendar = Calendar.objects.create_calendar(
            "calendar", user_contributed=True
        )
        self.person = Person.objects.create_insoumise(email="test@example.com")
        self.event = Event.objects.create(
            name="Event test", start_time=self.start_time, end_time=self.end_time
        )
        self.group1 = SupportGroup.objects.create(name="Nom")
        Membership.objects.create(
            person=self.person,
            supportgroup=self.group1,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.group2 = SupportGroup.objects.create(name="Nom")
        Membership.objects.create(
            person=self.person,
            supportgroup=self.group2,
            membership_type=Membership.MEMBERSHIP_TYPE_MEMBER,
        )

        self.organizer_config = OrganizerConfig(
            person=self.person, event=self.event, is_creator=True
        )

    def test_can_add_group_as_organizer(self):
        self.organizer_config.as_group = self.group1
        self.organizer_config.full_clean()

    def test_cannot_add_group_as_organizer_if_not_manager(self):
        self.organizer_config.as_group = self.group2
        with self.assertRaises(ValidationError):
            self.organizer_config.full_clean()


class EventSearchViewTestCase(TestCase):
    def setUp(self):
        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.subtype = EventSubtype.objects.create(
            label="sous-type",
            visibility=EventSubtype.VISIBILITY_ALL,
            type=EventSubtype.TYPE_PUBLIC_ACTION,
        )


class EventPagesTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise("test@test.com", create_role=True)
        self.other_person = Person.objects.create_insoumise(
            "other@test.fr", create_role=True
        )
        self.group = SupportGroup.objects.create(name="Group name")
        Membership.objects.create(
            supportgroup=self.group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.own_group = SupportGroup.objects.create(name="Own group name")
        Membership.objects.create(
            supportgroup=self.own_group,
            person=self.person,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )

        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.subtype = EventSubtype.objects.create(
            label="sous-type",
            description="Mon sous-type",
            default_description="GRANDIOSE",
            default_image="image.png",
            visibility=EventSubtype.VISIBILITY_ALL,
            type=EventSubtype.TYPE_PUBLIC_ACTION,
        )

        self.organized_event = Event.objects.create(
            name="Organized event",
            subtype=self.subtype,
            start_time=now - day,
            end_time=now - day + 4 * hour,
        )

        RSVP.objects.create(person=self.person, event=self.organized_event)
        OrganizerConfig.objects.create(
            event=self.organized_event, person=self.person, is_creator=True
        )

        self.organized_by_group_and_unrsvped_event = Event.objects.create_event(
            name="Organized by group and unrsvped event",
            subtype=self.subtype,
            organizer_person=self.other_person,
            organizer_group=self.own_group,
            start_time=now - day,
            end_time=now - day + 4 * hour,
        )

        self.rsvped_event = Event.objects.create(
            name="RSVPed event",
            subtype=self.subtype,
            start_time=now - 2 * day,
            end_time=now - 2 * day + 2 * hour,
            allow_guests=True,
        )

        RSVP.objects.create(person=self.person, event=self.rsvped_event)

        self.other_event = Event.objects.create(
            name="Other event",
            subtype=self.subtype,
            start_time=now - 3 * day,
            end_time=now - 3 * day + 4 * hour,
        )

        self.other_rsvp1 = RSVP.objects.create(
            person=self.other_person, event=self.rsvped_event
        )

        self.other_rsvp2 = RSVP.objects.create(
            person=self.other_person, event=self.other_event
        )

        self.past_event = Event.objects.create(
            name="past Event",
            subtype=self.subtype,
            start_time=now - 2 * day,
            end_time=now - 2 * day + 2 * hour,
            report_content="Ceci est un compte rendu de l'evenement",
            report_summary_sent=False,
        )

        self.futur_event = Event.objects.create(
            name="past Event",
            subtype=self.subtype,
            start_time=now + 2 * day,
            end_time=now + 2 * day + 2 * hour,
            report_content="Ceci est un compte rendu de l'evenement",
            report_summary_sent=False,
        )

        self.no_report_event = Event.objects.create(
            name="no report event",
            subtype=self.subtype,
            start_time=now + 2 * day,
            end_time=now + 2 * day + 2 * hour,
            report_content="",
            report_summary_sent=False,
        )

        self.already_sent_event = Event.objects.create(
            name="all ready sent event",
            subtype=self.subtype,
            start_time=now + 2 * day,
            end_time=now + 2 * day + 2 * hour,
            report_content="",
            report_summary_sent=True,
        )

        OrganizerConfig.objects.create(
            event=self.past_event, person=self.person, is_creator=True
        )
        OrganizerConfig.objects.create(
            event=self.futur_event, person=self.person, is_creator=True
        )
        OrganizerConfig.objects.create(
            event=self.no_report_event, person=self.person, is_creator=True
        )
        OrganizerConfig.objects.create(
            event=self.already_sent_event, person=self.person, is_creator=True
        )

        self.the_rsvp = RSVP.objects.create(person=self.person, event=self.past_event)

    def test_cannot_access_upload_image_page_if_not_rsvp_or_organizer(self):
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse("upload_event_image", kwargs={"pk": self.other_event.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_can_access_upload_image_page_if_rsvp(self):
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse("upload_event_image", kwargs={"pk": self.rsvped_event.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_access_upload_image_page_if_organizer(self):
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse("upload_event_image", kwargs={"pk": self.organized_event.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_access_upload_image_page_if_manager_of_organizer_group(self):
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse(
                "upload_event_image",
                kwargs={"pk": self.organized_by_group_and_unrsvped_event.pk},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_see_public_event(self):
        res = self.client.get(
            reverse("view_event", kwargs={"pk": self.organized_event.pk})
        )

        self.assertContains(res, self.organized_event.name)

    def test_cannot_see_private_event_only_if_organizer(self):
        self.organized_event.visibility = Event.VISIBILITY_ORGANIZER
        self.organized_event.save()

        self.client.force_login(self.other_person.role)
        res = self.client.get(
            reverse("view_event", kwargs={"pk": self.organized_event.pk})
        )
        self.assertRedirects(
            res,
            reverse("short_code_login")
            + "?next="
            + reverse("view_event", kwargs={"pk": self.organized_event.pk}),
        )

        self.client.force_login(self.person.role)
        res = self.client.get(
            reverse("view_event", kwargs={"pk": self.organized_event.pk})
        )
        self.assertContains(res, self.organized_event.name)

    def test_cannot_see_admin_event(self):
        self.organized_event.visibility = Event.VISIBILITY_ADMIN
        self.organized_event.save()

        self.client.force_login(self.person.role)
        res = self.client.get(
            reverse("view_event", kwargs={"pk": self.organized_event.pk})
        )
        self.assertNotContains(
            res, self.organized_event.name, status_code=status.HTTP_410_GONE
        )

    @mock.patch("agir.events.views.event_views.send_event_report")
    def test_can_not_send_event_report_when_nocondition(self, send_event_report):
        """Si une des conditions manque, l'envoi du mail ne se fait pas.

        Les conditions sont : le mail n'a jamais été envoyé, l'événement est passé,
        le compte-rendu n'est pas vide."""
        self.client.force_login(self.person.role)
        response = self.client.post(
            reverse("send_event_report", kwargs={"pk": self.no_report_event.pk})
        )
        send_event_report.delay.assert_not_called()
        response = self.client.post(
            reverse("send_event_report", kwargs={"pk": self.futur_event.pk})
        )
        send_event_report.delay.assert_not_called()
        response = self.client.post(
            reverse("send_event_report", kwargs={"pk": self.already_sent_event.pk})
        )
        send_event_report.delay.assert_not_called()


class RSVPTestCase(TestCase):
    # TODO: refactor this test case... too big
    def setUp(self):
        self.person = Person.objects.create_insoumise("test@test.com", create_role=True)
        self.already_rsvped = Person.objects.create_insoumise(
            "test2@test.com", create_role=True
        )

        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.simple_event = Event.objects.create(
            name="Simple Event",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

        person_form_kwargs = {
            "title": "Formulaire événement",
            "slug": "formulaire-evenement",
            "description": "Ma description complexe",
            "confirmation_note": "Ma note de fin",
            "main_question": "QUESTION PRINCIPALE",
            "custom_fields": [
                {
                    "title": "Détails",
                    "fields": [
                        {
                            "id": "custom-field",
                            "type": "short_text",
                            "label": "Mon label",
                            "person_field": True,
                        },
                        {
                            "id": "price",
                            "type": "integer",
                            "label": "Prix",
                            "required": False,
                        },
                    ],
                }
            ],
        }
        self.subscription_form = PersonForm.objects.create(**person_form_kwargs)
        self.subscription_form2 = PersonForm.objects.create(
            **{**person_form_kwargs, "slug": "formulaire-evenement2"}
        )
        self.form_event = Event.objects.create(
            name="Other event",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
            subscription_form=self.subscription_form,
        )

        self.simple_paying_event = Event.objects.create(
            name="Paying event",
            start_time=now + 10 * day,
            end_time=now + 10 * day + 4 * hour,
            payment_parameters={"price": 1000},
        )

        self.form_paying_event = Event.objects.create(
            name="Paying event",
            start_time=now + 10 * day,
            end_time=now + 10 * day + 4 * hour,
            payment_parameters={"price": 1000},
            subscription_form=self.subscription_form2,
        )

        RSVP.objects.create(person=self.already_rsvped, event=self.simple_event)
        RSVP.objects.create(
            person=self.already_rsvped,
            event=self.form_event,
            form_submission=PersonFormSubmission.objects.create(
                person=self.already_rsvped,
                form=self.subscription_form,
                data={"custom-field": "custom value"},
            ),
        )
        RSVP.objects.create(person=self.already_rsvped, event=self.simple_paying_event)
        RSVP.objects.create(
            person=self.already_rsvped,
            event=self.form_paying_event,
            form_submission=PersonFormSubmission.objects.create(
                person=self.already_rsvped,
                form=self.subscription_form,
                data={"custom-field": "custom value"},
            ),
        )

        self.billing_information = {
            "first_name": "Marc",
            "last_name": "Frank",
            "location_address1": "4 rue de Chaume",
            "location_address2": "",
            "location_zip": "33000",
            "location_city": "Bordeaux",
            "location_country": "FR",
            "contact_phone": "06 45 78 98 45",
        }

    def test_can_view_rsvp(self):
        self.client.force_login(self.already_rsvped.role)

        url = reverse("api_event_details", kwargs={"pk": self.simple_event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual("CO", response.json()["rsvp"])
        self.assertEqual(1, self.simple_event.participants)

    def test_cannot_rsvp_if_max_participants_reached(self):
        self.client.force_login(self.person.role)

        self.simple_event.max_participants = 1
        self.simple_event.save()

        url = reverse("view_event", kwargs={"pk": self.simple_event.pk})

        # cannot view the RSVP button
        response = self.client.get(url)
        self.assertNotContains(response, "Participer à cet événement")

        # cannot rsvp even when posting the form
        response = self.client.post(
            reverse("rsvp_event", kwargs={"pk": self.simple_event.pk})
        )
        self.assertRedirects(response, url)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.ERROR)
        self.assertIn("complet.", msgs[0].message)

        self.assertEqual(1, self.simple_event.participants)

    @mock.patch("agir.events.actions.rsvps.send_guest_confirmation")
    def test_can_add_guest_to_simple_event(self, guest_notification):
        self.client.force_login(self.already_rsvped.role)
        self.simple_event.allow_guests = True
        self.simple_event.save()

        response = self.client.post(
            reverse("rsvp_event", kwargs={"pk": self.simple_event.pk}),
            data={"guests": 1},
        )
        self.assertRedirects(
            response, reverse("view_event", kwargs={"pk": self.simple_event.pk})
        )
        self.assertEqual(2, self.simple_event.participants)

        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(msgs[0].level, messages.SUCCESS)

        guest_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.already_rsvped, event=self.simple_event)
        self.assertEqual(guest_notification.delay.call_args[0][0], rsvp.pk)

    def test_cannot_add_guest_if_forbidden_for_event(self):
        self.client.force_login(self.already_rsvped.role)

        response = self.client.post(
            reverse("rsvp_event", kwargs={"pk": self.simple_event.pk}),
            data={"guests": 1},
        )

        self.assertRedirects(
            response, reverse("view_event", kwargs={"pk": self.simple_event.pk})
        )
        self.assertEqual(1, self.simple_event.participants)

        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(msgs[0].level, messages.ERROR)

    def test_cannot_add_guest_for_simple_event_if_max_participants_reached(self):
        self.client.force_login(self.already_rsvped.role)

        self.simple_event.allow_guests = True
        self.simple_event.max_participants = 1
        self.simple_event.save()

        response = self.client.post(
            reverse("rsvp_event", kwargs={"pk": self.simple_event.pk}),
            data={"guests": 1},
        )

        self.assertRedirects(
            response, reverse("view_event", kwargs={"pk": self.simple_event.pk})
        )
        self.assertEqual(1, self.simple_event.participants)

        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(msgs[0].level, messages.ERROR)

    @mock.patch("agir.events.actions.rsvps.send_rsvp_notification")
    def test_can_rsvp_to_form_event(self, rsvp_notification):
        self.client.force_login(self.person.role)

        event_url = reverse("view_event", kwargs={"pk": self.form_event.pk})
        rsvp_url = reverse("rsvp_event", kwargs={"pk": self.form_event.pk})

        response = self.client.get(rsvp_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            rsvp_url, data={"custom-field": "another custom value"}
        )
        self.assertRedirects(response, event_url)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(msgs[0].level, messages.SUCCESS)

        self.person.refresh_from_db()
        self.assertIn(self.person, self.form_event.attendees.all())
        self.assertEqual(self.person.meta["custom-field"], "another custom value")
        self.assertEqual(2, self.form_event.participants)

        rsvp_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.person, event=self.form_event)
        self.assertEqual(rsvp_notification.delay.call_args[0][0], rsvp.pk)

    def test_can_edit_rsvp_form(self):
        self.client.force_login(self.person.role)

        rsvp_url = reverse("rsvp_event", kwargs={"pk": self.form_event.pk})
        self.client.post(rsvp_url, data={"custom-field": "another custom value"})

        res = self.client.get(rsvp_url)
        self.assertNotContains(res, "Modifier mon inscription")

        self.form_event.subscription_form.editable = True
        self.form_event.subscription_form.save()
        res = self.client.get(rsvp_url)
        self.assertContains(res, "Modifier ces informations")

    @mock.patch("agir.events.actions.rsvps.send_guest_confirmation")
    def test_can_add_guest_to_form_event(self, guest_confirmation):
        self.form_event.allow_guests = True
        self.form_event.save()

        self.form_event.subscription_form.editable = True
        self.form_event.subscription_form.save()

        self.client.force_login(self.already_rsvped.role)

        event_url = reverse("view_event", kwargs={"pk": self.form_event.pk})
        rsvp_url = reverse("rsvp_event", kwargs={"pk": self.form_event.pk})

        response = self.client.get(rsvp_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            rsvp_url, data={"custom-field": "another custom value", "is_guest": "yes"}
        )
        self.assertRedirects(response, event_url)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(msgs[0].level, messages.SUCCESS)

        self.assertEqual(2, self.form_event.participants)

        guest_confirmation.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.already_rsvped, event=self.form_event)
        self.assertNotEqual(
            rsvp.form_submission_id, rsvp.identified_guests.first().submission_id
        )
        self.assertEqual(guest_confirmation.delay.call_args[0][0], rsvp.pk)

    def test_cannot_add_guest_to_form_event_if_forbidden(self):
        self.client.force_login(self.already_rsvped.role)

        event_url = reverse("view_event", kwargs={"pk": self.form_event.pk})
        rsvp_url = reverse("rsvp_event", kwargs={"pk": self.form_event.pk})

        response = self.client.post(
            rsvp_url, data={"custom-field": "another custom value", "is_guest": "yes"}
        )
        self.assertRedirects(response, event_url)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(msgs[0].level, messages.ERROR)

        self.assertEqual(1, self.form_event.participants)

    @mock.patch("django.db.transaction.on_commit")
    def test_can_rsvp_to_simple_paying_event(self, on_commit):
        self.client.force_login(self.person.role)

        response = self.client.post(
            reverse("rsvp_event", args=[self.simple_paying_event.pk])
        )
        self.assertRedirects(response, reverse("pay_event"))

        response = self.client.get(reverse("pay_event"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response, f'name="event" value="{self.simple_paying_event.pk}"'
        )
        self.assertContains(response, 'name="submission"')
        self.assertNotContains(response, 'name="submission" value')
        self.assertContains(response, f'name="is_guest" value="False"')

        response = self.client.post(
            reverse("pay_event"),
            data={
                "event": self.simple_paying_event.pk,
                "payment_mode": "check_events",
                **self.billing_information,
            },
        )

        payment = Payment.objects.get()
        self.assertRedirects(response, front_url("payment_page", args=(payment.pk,)))

        # fake payment confirmation
        complete_payment(payment)
        event_notification_listener(payment)

        self.assertIn(self.person, self.simple_paying_event.attendees.all())

        on_commit.assert_called_once()
        cb = on_commit.call_args[0][0]
        self.assertIsInstance(cb, partial)
        self.assertEqual(cb.func, send_rsvp_notification.delay)
        rsvp = RSVP.objects.get(person=self.person, event=self.simple_paying_event)
        self.assertEqual(cb.args[0], rsvp.pk)

    @mock.patch("django.db.transaction.on_commit")
    def test_can_add_guest_to_simple_paying_event(self, on_commit):
        self.simple_paying_event.allow_guests = True
        self.simple_paying_event.save()
        self.client.force_login(self.already_rsvped.role)
        session = self.client.session

        response = self.client.post(
            reverse("rsvp_event", args=[self.simple_paying_event.pk])
        )
        # check that the guest status is well transfered
        self.assertEqual(session["is_guest"], True)
        self.assertRedirects(response, reverse("pay_event"))

        response = self.client.get(reverse("pay_event"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response, f'name="event" value="{self.simple_paying_event.pk}"'
        )
        self.assertContains(response, 'name="submission"')
        self.assertNotContains(response, 'name="submission" value')
        self.assertContains(response, f'name="is_guest" value="True"')

        response = self.client.post(
            reverse("pay_event"),
            data={
                "event": self.simple_paying_event.pk,
                "payment_mode": "check_events",
                "is_guest": "yes",
                **self.billing_information,
            },
        )

        payment = Payment.objects.get()
        self.assertRedirects(response, front_url("payment_page", args=(payment.pk,)))

        complete_payment(payment)
        event_notification_listener(payment)

        on_commit.assert_called_once()
        cb = on_commit.call_args[0][0]
        self.assertIsInstance(cb, partial)
        self.assertEqual(cb.func, send_guest_confirmation.delay)

        rsvp = RSVP.objects.get(
            person=self.already_rsvped, event=self.simple_paying_event
        )
        self.assertEqual(cb.args[0], rsvp.pk)

    @mock.patch("django.db.transaction.on_commit")
    def test_can_rsvp_to_form_paying_event(self, on_commit):
        self.client.force_login(self.person.role)

        response = self.client.get(
            reverse("rsvp_event", args=[self.form_paying_event.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("rsvp_event", args=[self.form_paying_event.pk]),
            data={"custom-field": "my own custom value"},
        )
        self.assertRedirects(response, reverse("pay_event"))

        submission = PersonFormSubmission.objects.get(
            person=self.person, form=self.subscription_form2
        )

        response = self.client.get(reverse("pay_event"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response, f'name="event" value="{self.form_paying_event.pk}"'
        )
        self.assertContains(response, f'name="submission" value="{submission.pk}"')
        self.assertContains(response, f'name="is_guest" value="False"')

        response = self.client.post(
            reverse("pay_event"),
            data={
                "event": self.form_paying_event.pk,
                "submission": submission.pk,
                "payment_mode": "check_events",
                **self.billing_information,
            },
        )

        payment = Payment.objects.get()
        self.assertRedirects(response, front_url("payment_page", args=(payment.pk,)))

        # fake payment confirmation
        complete_payment(payment)
        event_notification_listener(payment)

        self.assertIn(self.person, self.form_paying_event.attendees.all())

        on_commit.assert_called_once()
        cb = on_commit.call_args[0][0]
        self.assertIsInstance(cb, partial)
        self.assertEqual(cb.func, send_rsvp_notification.delay)
        rsvp = RSVP.objects.get(person=self.person, event=self.form_paying_event)
        self.assertEqual(cb.args[0], rsvp.pk)

        response = self.client.get(
            reverse("rsvp_event", args=[self.form_paying_event.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "my own custom value")

    @mock.patch("django.db.transaction.on_commit")
    def test_can_add_guest_to_form_paying_event(self, on_commit):
        self.form_paying_event.allow_guests = True
        self.form_paying_event.save()
        self.client.force_login(self.already_rsvped.role)

        # obligé de faire ça pour que la session soit préservée
        session = self.client.session

        response = self.client.get(
            reverse("rsvp_event", args=[self.form_paying_event.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("rsvp_event", args=[self.form_paying_event.pk]),
            data={"custom-field": "my guest custom value", "is_guest": "yes"},
        )
        self.assertRedirects(response, reverse("pay_event"))

        submission = PersonFormSubmission.objects.filter(
            person=self.already_rsvped
        ).latest("created")

        response = self.client.get(reverse("pay_event"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(
            response, f'name="event" value="{self.form_paying_event.pk}"'
        )
        self.assertContains(response, f'name="submission" value="{submission.pk}"')
        self.assertContains(response, f'name="is_guest" value="True"')

        response = self.client.post(
            reverse("pay_event"),
            data={
                "event": self.form_paying_event.pk,
                "submission": submission.pk,
                "payment_mode": "check_events",
                "is_guest": "yes",
                **self.billing_information,
            },
        )

        payment = Payment.objects.get()
        self.assertRedirects(response, front_url("payment_page", args=(payment.pk,)))

        complete_payment(payment)
        event_notification_listener(payment)

        self.assertEqual(2, self.form_paying_event.participants)

        on_commit.assert_called_once()
        cb = on_commit.call_args[0][0]
        self.assertIsInstance(cb, partial)
        self.assertEqual(cb.func, send_guest_confirmation.delay)

        rsvp = RSVP.objects.get(
            person=self.already_rsvped, event=self.form_paying_event
        )
        self.assertEqual(cb.args[0], rsvp.pk)

        response = self.client.get(
            reverse("rsvp_event", args=[self.form_paying_event.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "my guest custom value")

    def test_can_retry_payment_on_rsvp(self):
        self.client.force_login(self.person.role)

        self.client.post(reverse("rsvp_event", args=[self.simple_paying_event.pk]))
        response = self.client.post(
            reverse("pay_event"),
            data={
                "event": self.simple_paying_event.pk,
                "payment_mode": "system_pay",
                **self.billing_information,
            },
        )

        payment = Payment.objects.get()
        self.assertRedirects(response, front_url("payment_page", args=[payment.pk]))

        response = self.client.get(reverse("payment_retry", args=[payment.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_rsvp_if_not_authorized_for_form(self):
        tag = PersonTag.objects.create(label="tag")
        self.subscription_form.required_tags.add(tag)
        self.subscription_form.unauthorized_message = "SENTINEL"
        self.subscription_form.save()

        self.client.force_login(self.person.role)

        event_url = reverse("view_event", kwargs={"pk": self.form_event.pk})
        rsvp_url = reverse("rsvp_event", kwargs={"pk": self.form_event.pk})

        response = self.client.get(rsvp_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "SENTINEL")

        response = self.client.post(
            rsvp_url, data={"custom-field": "another custom value"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("form", response.context_data)

    @mock.patch("agir.events.actions.rsvps.send_rsvp_notification")
    def test_can_rsvp_if_authorized_for_form(self, rsvp_notification):
        tag = PersonTag.objects.create(label="tag")
        self.person.tags.add(tag)
        self.subscription_form.required_tags.add(tag)
        self.subscription_form.unauthorized_message = "SENTINEL"
        self.subscription_form.save()

        self.client.force_login(self.person.role)

        event_url = reverse("view_event", kwargs={"pk": self.form_event.pk})
        rsvp_url = reverse("rsvp_event", kwargs={"pk": self.form_event.pk})

        response = self.client.get(rsvp_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotContains(response, "SENTINEL")
        self.assertIn("form", response.context_data)

        response = self.client.post(
            rsvp_url, data={"custom-field": "another custom value"}
        )
        self.assertRedirects(response, event_url)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(msgs[0].level, messages.SUCCESS)

        self.person.refresh_from_db()
        self.assertIn(self.person, self.form_event.attendees.all())
        self.assertEqual(self.person.meta["custom-field"], "another custom value")
        self.assertEqual(2, self.form_event.participants)

        rsvp_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.person, event=self.form_event)
        self.assertEqual(rsvp_notification.delay.call_args[0][0], rsvp.pk)

    def test_cannot_rsvp_if_form_is_closed(self):
        self.client.force_login(self.person.role)
        self.form_event.subscription_form.end_time = (
            timezone.now() - timezone.timedelta(days=1)
        )
        self.form_event.subscription_form.save()

        res = self.client.get(reverse("rsvp_event", kwargs={"pk": self.form_event.pk}))
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

        res = self.client.post(
            reverse("rsvp_event", kwargs={"pk": self.form_event.pk}),
            data={"custom-field": "another custom value"},
        )
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

    def test_cannot_rsvp_if_form_is_yet_to_open(self):
        self.client.force_login(self.person.role)
        self.form_event.subscription_form.start_time = (
            timezone.now() + timezone.timedelta(days=1)
        )
        self.form_event.subscription_form.save()

        res = self.client.get(reverse("rsvp_event", kwargs={"pk": self.form_event.pk}))
        self.assertContains(res, "est pas encore ouvert.")

        res = self.client.post(
            reverse("rsvp_event", kwargs={"pk": self.form_event.pk}),
            data={"custom-field": "another custom value"},
        )
        self.assertContains(res, "est pas encore ouvert.")

    @mock.patch("agir.events.actions.rsvps.send_rsvp_notification")
    def test_not_billed_if_free_pricing_to_zero(self, rsvp_notification):
        self.client.force_login(self.person.role)

        self.form_event.payment_parameters = {"free_pricing": "price"}
        self.form_event.save()

        event_url = reverse("view_event", kwargs={"pk": self.form_event.pk})
        rsvp_url = reverse("rsvp_event", kwargs={"pk": self.form_event.pk})

        response = self.client.get(rsvp_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            rsvp_url, data={"custom-field": "another custom value", "price": "0"}
        )
        self.assertRedirects(response, event_url)
        msgs = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(msgs[0].level, messages.SUCCESS)

        self.person.refresh_from_db()
        self.assertIn(self.person, self.form_event.attendees.all())
        self.assertEqual(self.person.meta["custom-field"], "another custom value")
        self.assertEqual(2, self.form_event.participants)

        rsvp_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.person, event=self.form_event)
        self.assertEqual(rsvp_notification.delay.call_args[0][0], rsvp.pk)


class PricingTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise("test@test.com")

        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        self.event = Event.objects.create(
            name="Simple Event",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
        )

    def test_pricing_display(self):
        self.assertEqual(self.event.get_price_display(), None)

        self.event.payment_parameters = {"price": 1000}
        self.assertEqual(self.event.get_price_display(), "10,00 €")

        self.event.payment_parameters = {"free_pricing": "value"}
        self.assertEqual(self.event.get_price_display(), "Prix libre")

        self.event.payment_parameters = {
            "mappings": [
                {
                    "mapping": [
                        {"values": ["A"], "price": 100},
                        {"values": ["B"], "price": 200},
                    ],
                    "fields": ["f"],
                }
            ]
        }
        self.assertEqual(self.event.get_price_display(), "de 1,00 à 2,00 €")

        self.event.payment_parameters["price"] = 1000
        self.assertEqual(self.event.get_price_display(), "de 11,00 à 12,00 €")

        self.event.payment_parameters["free_pricing"] = "value"
        self.assertEqual(
            self.event.get_price_display(), "de 11,00 à 12,00 € + montant libre"
        )

    def test_simple_pricing_event(self):
        self.event.payment_parameters = {"price": 1000}
        self.assertEqual(self.event.get_price(), 1000)

        self.event.payment_parameters["mappings"] = [
            {
                "mapping": [
                    {"values": ["A"], "price": 100},
                    {"values": ["B"], "price": 200},
                ],
                "fields": ["mapping_field"],
            }
        ]
        sub = PersonFormSubmission()

        sub.data = {"mapping_field": "A"}
        self.assertEqual(self.event.get_price(sub.data), 1100)
        sub.data = {"mapping_field": "B"}
        self.assertEqual(self.event.get_price(sub.data), 1200)

        self.event.payment_parameters["free_pricing"] = "price_field"

        sub.data = {"mapping_field": "A", "price_field": 5}
        self.assertEqual(self.event.get_price(sub.data), 1600)
        sub.data = {"mapping_field": "B", "price_field": 15}
        self.assertEqual(self.event.get_price(sub.data), 2700)


class CalendarPageTestCase(TestCase):
    def setUp(self):
        self.calendar = Calendar.objects.create(name="My calendar", slug="my_calendar")

        now = timezone.now()
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)

        for i in range(20):
            e = Event.objects.create(
                name="Event {}".format(i),
                start_time=now + i * day,
                end_time=now + i * day + hour,
            )
            CalendarItem.objects.create(event=e, calendar=self.calendar)

    def test_can_view_page(self):
        # can show first page
        res = self.client.get("/agenda/my_calendar/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, 'href="/agenda/my_calendar/?page=2')
        self.assertNotContains(res, 'href="/agenda/my_calendar/?page=1')

        # can display second page
        res = self.client.get("/agenda/my_calendar/?page=2")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotContains(res, 'href="/agenda/my_calendar/?page=2')
        self.assertContains(res, 'href="/agenda/my_calendar/?page=1')


class ExternalRSVPTestCase(TestCase):
    def setUp(self):
        self.geocode_element = patch("agir.lib.tasks.geocode_element", autospec=True)
        self.geocode_element.start()
        self.addCleanup(self.geocode_element.stop)

        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.person = Person.objects.create_person(
            "test@test.com", is_political_support=True
        )
        self.subtype = EventSubtype.objects.create(
            type=EventSubtype.TYPE_PUBLIC_ACTION, allow_external=True
        )
        self.event = Event.objects.create(
            name="Simple Event",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
            subtype=self.subtype,
        )

    def test_cannot_external_rsvp_if_does_not_allow_external(self):
        self.subtype.allow_external = False
        self.subtype.save()
        subscription_token = subscription_confirmation_token_generator.make_token(
            email="test1@test.com"
        )
        query_args = {"email": "test1@test.com", "token": subscription_token}
        self.client.get(
            reverse("external_rsvp_event", args=[self.event.pk])
            + "?"
            + urlencode(query_args)
        )

        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(email="test1@test.com")

    def test_can_rsvp(self):
        res = self.client.get(reverse("view_event", args=[self.event.pk]))

        self.client.post(
            reverse("external_rsvp_event", args=[self.event.pk]),
            data={"email": self.person.email},
        )
        self.assertEqual(self.person.rsvps.all().count(), 0)

        subscription_token = subscription_confirmation_token_generator.make_token(
            email=self.person.email
        )
        query_args = {"email": self.person.email, "token": subscription_token}
        self.client.get(
            reverse("external_rsvp_event", args=[self.event.pk])
            + "?"
            + urlencode(query_args)
        )

        self.assertEqual(self.person.rsvps.first().event, self.event)

    def test_can_rsvp_without_account(self):
        self.client.post(
            reverse("external_rsvp_event", args=[self.event.pk]),
            data={"email": "test1@test.com"},
        )

        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(email="test1@test.com")

        subscription_token = subscription_confirmation_token_generator.make_token(
            email="test1@test.com"
        )
        query_args = {"email": "test1@test.com", "token": subscription_token}
        self.client.get(
            reverse("external_rsvp_event", args=[self.event.pk])
            + "?"
            + urlencode(query_args)
        )

        self.assertEqual(
            Person.objects.get(email="test1@test.com").rsvps.first().event, self.event
        )


class JitsiViewTestCase(FakeDataMixin, TestCase):
    def reserve_room(self):
        return self.client.post(
            reverse("jitsi_reservation"),
            data={"name": "testroom1", "start_time": timezone.now().isoformat()},
        )

    def test_reservation_404_when_no_meeting(self):
        res = self.reserve_room()

        self.assertEqual(res.status_code, 404)

    def test_reservation_403_when_not_started(self):
        JitsiMeeting.objects.create(
            domain="lol",
            room_name="testroom1",
            event=self.data["events"]["user1_event1"],
        )

        res = self.reserve_room()

        self.assertEqual(res.status_code, 403)

    def test_reservation_200_when_started(self):
        event = self.data["events"]["user1_event1"]
        event.start_time = timezone.now() - timedelta(hours=1)
        event.save()

        JitsiMeeting.objects.create(
            domain="lol",
            room_name="testroom1",
            event=self.data["events"]["user1_event1"],
        )

        res = self.reserve_room()

        self.assertEqual(res.status_code, 200)

    def test_reservation_200_when_no_event(self):
        JitsiMeeting.objects.create(domain="lol", room_name="testroom1")

        res = self.reserve_room()

        self.assertEqual(res.status_code, 200)


class DoNotListEventTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name="Un événement qui sera non listé",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=4),
            do_not_list=False,
            coordinates=Point(2.349_722, 48.853_056),  # ND de Paris
        )

        self.person = Person.objects.create_insoumise(
            "test@test.com",
            create_role=True,
            coordinates=Point(2.349_722, 48.853_056),  # ND de Paris
        )
        self.client.force_login(self.person.role)

    def test_unlisted_events_are_not_in_sitemap(self):
        response = self.client.get(
            reverse(
                "django.contrib.sitemaps.views.sitemap", kwargs={"section": "events"}
            )
        )
        self.assertContains(response, self.event.pk)

        self.event.do_not_list = True
        self.event.save()

        response = self.client.get(
            reverse(
                "django.contrib.sitemaps.views.sitemap", kwargs={"section": "events"}
            )
        )
        self.assertNotContains(response, self.event.pk)

    def test_unlisted_events_are_not_in_event_map(self):
        events = EventMapView.queryset.filter(pk=self.event.pk)
        self.assertTrue(len(events) == 1)

        self.event.do_not_list = True
        self.event.save()

        events = EventMapView.queryset.filter(pk=self.event.pk)
        self.assertTrue(len(events) == 0)

    def test_unlisted_events_are_not_in_search_event_result(self):
        response = self.client.get(
            reverse("search_event"), data={"text_query": "sera non listé"}
        )
        self.assertContains(response, "Un événement qui sera non listé")

        self.event.do_not_list = True
        self.event.save()

        response = self.client.get(
            reverse("search_event"), data={"text_query": "sera non listé"}
        )
        self.assertNotContains(response, "Un événement qui sera non listé")


def get_search_url(search):
    return "{}?{}".format(reverse("search_event"), urlencode({"q": search}))


class SearchEventTestCase(TestCase):
    def setUp(self):
        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        self.day = day = timezone.timedelta(days=1)
        self.hour = hour = timezone.timedelta(hours=1)
        self.person = Person.objects.create_insoumise(
            "test@test.com",
            create_role=True,
            coordinates=Point(2.382_486, 48.888_022),  # Paris, 19eme
        )
        self.group = SupportGroup.objects.create(name="ChaosComputerClub")

        self.event = Event.objects.create(
            name="Pas de pays pour le vieil homme",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
            description="La gargantuesque description garantit une affluence à profusion!! ## CommonWord ##",
            location_name="Le meilleur endroit du monde",
            coordinates=Point(2.343_007, 48.886_646),  # Paris, Sacré-Cœur
        )

        self.event_past = Event.objects.create(
            name="Événement simple",
            start_time=now - 3 * day,
            end_time=now + 3 * day + 4 * hour,
            report_content="Il est essentiel d'écrire la légende des événements passés. Les mots s'envolent, les écrits restes. ## CommonWord ##",
            coordinates=Point(4.804_881, 43.953_847),  # Avignon, le fameux pont
        )

        self.organizer_config = OrganizerConfig.objects.create(
            event=self.event, person=self.person, as_group=self.group
        )
        OrganizerConfig.objects.create(event=self.event_past, person=self.person)
        self.client.force_login(self.person.role)

    def test_find_event_by_name(self):
        response = self.client.get(get_search_url("vieil homme"), follow=True)
        self.assertContains(response, "Pas de pays pour le vieil homme")

    def test_find_event_by_description(self):
        response = self.client.get(get_search_url("gargantuesque profusion"))
        self.assertContains(response, "Pas de pays pour le vieil homme")

    def test_find_event_by_report(self):
        response = self.client.get(get_search_url("écrire"))
        self.assertContains(response, "Événement simple")

    def test_find_event_by_location_name(self):
        response = self.client.get(get_search_url("meilleur endroit"))
        self.assertContains(response, "Pas de pays pour le vieil homme")

    # def test_find_event_in_time_interval(self):
    #     tz = timezone.get_default_timezone()
    #
    #     # avec juste une date minimum
    #     response = self.client.get(
    #         get_search_url("Pas de pays pour le vieil homme", min_date=self.now.date())
    #     )
    #     self.assertContains(response, "Le meilleur endroit du monde")
    #
    #     # avec juste une date maximum
    #     response = self.client.get(
    #         get_search_url(
    #             "Pas de pays pour le vieil homme",
    #             max_date=(self.now + 5 * self.day).date(),
    #         )
    #     )
    #     self.assertContains(response, "Le meilleur endroit du monde")
    #
    #     # dans un interval de 2 dates
    #     response = self.client.get(
    #         get_search_url(
    #             "pays homme",
    #             min_date=self.now.strftime("%d/%m/%Y"),
    #             date_end=(self.now + 5 * self.day).date(),
    #         )
    #     )
    #     self.assertContains(response, "Le meilleur endroit du monde")

    def test_event_are_indexed_after_created(self):
        response = self.client.get(get_search_url("incroyables"))
        self.assertContains(response, "Aucun événement ne correspond à votre recherche")
        event = Event.objects.create(
            name="Incroyable happening",
            start_time=self.now + self.day,
            end_time=self.now + self.day + 2 * self.hour,
            coordinates=Point(2.349_722, 48.853_056, srid=4326),  # ND de Paris,
            visibility="P",
        )
        response = self.client.get(get_search_url("incroyables"))
        self.assertContains(response, "Incroyable happening")
        self.assertNotContains(response, "Aucun événement ne correspond à votre")

    def test_event_update_content(self):
        self.event.name = "nouveau nom, nouvelle vie"
        self.event.description = "Ceci est une description"
        self.event.save()
        response = self.client.get(get_search_url("description"))
        self.assertContains(response, "nouveau nom, nouvelle vie")

    # def test_dont_find_event_too_far(self):
    #     response = self.client.get(get_search_url("pays vieil homme"))
    #     self.assertContains(response, "Le meilleur endroit")
    #     response = self.client.get(get_search_url("pays vieil homme", distance_max="1"))
    #     self.assertNotContains(response, "Le meilleur endroit")

    def test_dont_find_event_after_change_its_visibility(self):
        response = self.client.get(get_search_url("pays vieil homme"))
        self.assertContains(response, "Le meilleur endroit")
        self.event.visibility = "G"
        self.event.save()
        response = self.client.get(get_search_url("pays vieil homme"))
        self.assertNotContains(response, "Le meilleur endroit")


class AcceptCoorganizationInvitationTestCase(TestCase):
    def setUp(self):
        self.organizer = Person.objects.create_person(
            "organizer@agir.test", create_role=True
        )
        self.event = Event.objects.create(
            name="Événement multi-groupe",
            start_time=timezone.now() + datetime.timedelta(days=4),
            end_time=timezone.now() + datetime.timedelta(days=4, hours=2),
            visibility=Event.VISIBILITY_PUBLIC,
        )
        OrganizerConfig.objects.create(
            person=self.organizer, event=self.event, is_creator=True
        )

        self.invited_group = SupportGroup.objects.create(name="Invitee")
        self.person = Person.objects.create_person("person@agir.test", create_role=True)
        Membership.objects.create(
            person=self.person,
            supportgroup=self.invited_group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        self.invitation = Invitation.objects.create(
            event=self.event,
            person_sender=self.event.organizers.first(),
            group=self.invited_group,
        )

        self.url = reverse(
            "accept_event_group_coorganization", kwargs={"pk": self.invitation.id}
        )

    def test_anonymous_cannot_accept_invitation(self):
        self.invitation.status = Invitation.STATUS_PENDING
        self.invitation.save()
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_PENDING)
        self.assertFalse(
            OrganizerConfig.objects.filter(
                event=self.event, as_group=self.invited_group
            ).exists()
        )

    def test_group_manager_cannot_accept_invitation(self):
        self.invitation.status = Invitation.STATUS_PENDING
        self.invitation.save()
        person = Person.objects.create_person("manager@agir.test", create_role=True)
        Membership.objects.create(
            person=person,
            supportgroup=self.invited_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.client.force_login(person.role)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_PENDING)
        self.assertFalse(
            OrganizerConfig.objects.filter(
                event=self.event, as_group=self.invited_group
            ).exists()
        )

    def test_cannot_accept_unexisting_invitation(self):
        self.invitation.status = Invitation.STATUS_PENDING
        self.invitation.save()
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse(
                "accept_event_group_coorganization",
                kwargs={"pk": 100 + self.invitation.id},
            )
        )
        self.assertEqual(response.status_code, 404)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_PENDING)
        self.assertFalse(
            OrganizerConfig.objects.filter(
                event=self.event, as_group=self.invited_group
            ).exists()
        )

    def test_cannot_accept_an_invitation_for_a_past_event(self):
        past_event = Event.objects.create(
            name="Événement passé",
            start_time=timezone.now() - datetime.timedelta(days=4, hours=1),
            end_time=timezone.now() - datetime.timedelta(days=4),
            visibility=Event.VISIBILITY_PUBLIC,
        )
        invitation = Invitation.objects.create(
            status=Invitation.STATUS_PENDING,
            person_sender=self.event.organizers.first(),
            group=self.invited_group,
            event=past_event,
        )
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse(
                "accept_event_group_coorganization",
                kwargs={"pk": invitation.id},
            )
        )
        self.assertEqual(response.status_code, 302)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, Invitation.STATUS_PENDING)
        self.assertFalse(
            OrganizerConfig.objects.filter(
                event=past_event, as_group=self.invited_group
            ).exists()
        )

    def test_group_referent_can_accept_invitation(self):
        self.invitation.status = Invitation.STATUS_PENDING
        self.invitation.save()
        self.client.force_login(self.person.role)
        self.assertFalse(
            OrganizerConfig.objects.filter(
                event=self.event, as_group=self.invited_group
            ).exists()
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_ACCEPTED)
        self.assertTrue(
            OrganizerConfig.objects.filter(
                event=self.event, as_group=self.invited_group
            ).exists()
        )


class RefuseCoorganizationInvitationTestCase(TestCase):
    def setUp(self):
        self.organizer = Person.objects.create_person(
            "organizer@agir.test", create_role=True
        )
        self.event = Event.objects.create(
            name="Événement multi-groupe",
            start_time=timezone.now() + datetime.timedelta(days=4),
            end_time=timezone.now() + datetime.timedelta(days=4, hours=2),
            visibility=Event.VISIBILITY_PUBLIC,
        )
        OrganizerConfig.objects.create(
            person=self.organizer, event=self.event, is_creator=True
        )

        self.invited_group = SupportGroup.objects.create(name="Invitee")
        self.person = Person.objects.create_person("person@agir.test", create_role=True)
        Membership.objects.create(
            person=self.person,
            supportgroup=self.invited_group,
            membership_type=Membership.MEMBERSHIP_TYPE_REFERENT,
        )
        self.invitation = Invitation.objects.create(
            event=self.event,
            person_sender=self.event.organizers.first(),
            group=self.invited_group,
        )

        self.url = reverse(
            "refuse_event_group_coorganization", kwargs={"pk": self.invitation.id}
        )

    def test_anonymous_cannot_refuse_invitation(self):
        self.invitation.status = Invitation.STATUS_PENDING
        self.invitation.save()
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_PENDING)

    def test_non_group_referent_cannot_refuse_invitation(self):
        self.invitation.status = Invitation.STATUS_PENDING
        self.invitation.save()
        person = Person.objects.create_person("manager@agir.test", create_role=True)
        Membership.objects.create(
            person=person,
            supportgroup=self.invited_group,
            membership_type=Membership.MEMBERSHIP_TYPE_MANAGER,
        )
        self.client.force_login(person.role)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_PENDING)

    def test_cannot_refuse_invitation_unexisting_invitation(self):
        self.invitation.status = Invitation.STATUS_PENDING
        self.invitation.save()
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse(
                "refuse_event_group_coorganization",
                kwargs={"pk": 100 + self.invitation.id},
            )
        )
        self.assertEqual(response.status_code, 404)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_PENDING)

    def test_group_manager_cannot_refuse_accepted_invitation(self):
        self.invitation.status = Invitation.STATUS_ACCEPTED
        self.invitation.save()
        self.client.force_login(self.person.role)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_ACCEPTED)

    def test_cannot_refuse_an_invitation_for_a_past_event(self):
        past_event = Event.objects.create(
            name="Événement passé",
            start_time=timezone.now() - datetime.timedelta(days=4, hours=1),
            end_time=timezone.now() - datetime.timedelta(days=4),
            visibility=Event.VISIBILITY_PUBLIC,
        )
        invitation = Invitation.objects.create(
            status=Invitation.STATUS_PENDING,
            person_sender=self.event.organizers.first(),
            group=self.invited_group,
            event=past_event,
        )
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse(
                "refuse_event_group_coorganization",
                kwargs={"pk": invitation.id},
            )
        )
        self.assertEqual(response.status_code, 302)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, Invitation.STATUS_PENDING)
        self.assertFalse(
            OrganizerConfig.objects.filter(
                event=past_event, as_group=self.invited_group
            ).exists()
        )

    def test_group_manager_can_refuse_pending_invitation(self):
        self.invitation.status = Invitation.STATUS_PENDING
        self.invitation.save()
        self.client.force_login(self.person.role)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.invitation.refresh_from_db()
        self.assertEqual(self.invitation.status, Invitation.STATUS_REFUSED)
