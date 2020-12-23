from functools import partial
from unittest import mock

from datetime import timedelta

from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.test import TestCase
from django.utils import timezone, formats
from django.utils.http import urlencode

from rest_framework.reverse import reverse
from rest_framework import status

from agir.authentication.tokens import subscription_confirmation_token_generator
from agir.carte.views import EventMapView
from agir.events.actions import legal
from agir.events.tasks import (
    notify_on_event_report,
    send_guest_confirmation,
    send_rsvp_notification,
)
from agir.groups.models import SupportGroup, Membership
from agir.lib.tests.mixins import FakeDataMixin
from agir.lib.utils import front_url
from agir.payments.actions.payments import complete_payment
from agir.payments.models import Payment
from agir.people.models import Person, PersonForm, PersonFormSubmission, PersonTag

from ..forms import EventForm
from ..models import (
    Event,
    Calendar,
    RSVP,
    OrganizerConfig,
    CalendarItem,
    EventSubtype,
    JitsiMeeting,
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
        Membership.objects.create(person=self.person, supportgroup=self.group2)

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
        self.event_insoumis = Event.objects.create(
            name="Event Insoumis",
            subtype=self.subtype,
            start_time=now + day,
            end_time=now + day + 4 * hour,
            for_users=Event.FOR_USERS_INSOUMIS,
        )
        self.event_2022 = Event.objects.create(
            name="Event NSP",
            subtype=self.subtype,
            start_time=now + day,
            end_time=now + day + 4 * hour,
            for_users=Event.FOR_USERS_2022,
        )

    def test_insoumise_persone_can_search_through_all_events(self):
        self.client.force_login(self.person_insoumise.role)
        res = self.client.get(reverse("search_event") + "?q=e")
        self.assertContains(res, self.event_insoumis.name)
        self.assertContains(res, self.event_2022.name)

    def test_2022_only_person_can_search_through_2022_events_only(self):
        self.client.force_login(self.person_2022.role)
        res = self.client.get(reverse("search_event") + "?q=e")
        self.assertNotContains(res, self.event_insoumis.name)
        self.assertContains(res, self.event_2022.name)


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
            start_time=now + day,
            end_time=now + day + 4 * hour,
            legal={legal.QUESTION_SALLE: True, legal.QUESTION_MATERIEL_CAMPAGNE: True},
        )

        OrganizerConfig.objects.create(
            event=self.organized_event, person=self.person, is_creator=True
        )

        self.rsvped_event = Event.objects.create(
            name="RSVPed event",
            subtype=self.subtype,
            start_time=now + 2 * day,
            end_time=now + 2 * day + 2 * hour,
            allow_guests=True,
        )

        RSVP.objects.create(person=self.person, event=self.rsvped_event)

        self.other_event = Event.objects.create(
            name="Other event",
            subtype=self.subtype,
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
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

    @mock.patch.object(EventForm, "geocoding_task")
    @mock.patch("agir.events.forms.send_event_changed_notification")
    def test_can_modify_organized_event(
        self, patched_send_notification, patched_geocode
    ):
        self.client.force_login(self.person.role)
        response = self.client.get(
            reverse("edit_event", kwargs={"pk": self.organized_event.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse("edit_event", kwargs={"pk": self.organized_event.pk}),
            data={
                "name": "New Name",
                "start_time": formats.localize_input(
                    self.now + timezone.timedelta(hours=2), "%d/%m/%Y %H:%M"
                ),
                "end_time": formats.localize_input(
                    self.now + timezone.timedelta(hours=4), "%d/%m/%Y %H:%M"
                ),
                "contact_name": "Arthur",
                "contact_email": "a@ziefzji.fr",
                "contact_phone": "06 06 06 06 06",
                "location_name": "somewhere",
                "location_address1": "over",
                "location_zip": "27492",
                "location_city": "rainbow",
                "location_country": "FR",
                "description": "New description",
                "notify": "on",
                "as_group": self.group.pk,
            },
        )

        # the form redirects to the event manage page on success
        self.assertRedirects(
            response, reverse("manage_event", kwargs={"pk": self.organized_event.pk})
        )

        # accessing the messages: see https://stackoverflow.com/a/14909727/1122474
        messages = list(response.wsgi_request._messages)

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level_tag, "success")

        # send_support_group_changed_notification.delay should have been called once, with the pk of the group as
        # first argument, and the changes as the second
        patched_send_notification.delay.assert_called_once()
        args = patched_send_notification.delay.call_args[0]

        self.assertEqual(args[0], self.organized_event.pk)
        self.assertCountEqual(
            args[1],
            [
                "name",
                "start_time",
                "end_time",
                "contact_name",
                "contact_email",
                "contact_phone",
                "location_name",
                "location_address1",
                "location_zip",
                "location_city",
                "description",
                "as_group",
            ],
        )

        patched_geocode.delay.assert_called_once()
        args = patched_geocode.delay.call_args[0]

        self.assertEqual(args[0], self.organized_event.pk)
        self.assertIn(self.group, self.organized_event.organizers_groups.all())

    def test_cannot_modify_rsvp_event(self):
        self.client.force_login(self.person.role)

        # manage_page
        response = self.client.get(
            reverse("manage_event", kwargs={"pk": self.rsvped_event.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # get edit page
        response = self.client.get(
            reverse("edit_event", kwargs={"pk": self.rsvped_event.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # post edit page
        response = self.client.post(
            reverse("edit_event", kwargs={"pk": self.rsvped_event.pk}),
            data={
                "name": "New Name",
                "start_time": formats.localize_input(
                    timezone.now() + timezone.timedelta(hours=2), "%d/%m/%Y %H:%M"
                ),
                "end_time": formats.localize_input(
                    timezone.now() + timezone.timedelta(hours=4), "%d/%m/%Y %H:%M"
                ),
                "contact_name": "Arthur",
                "contact_email": "a@ziefzji.fr",
                "contact_phone": "06 06 06 06 06",
                "location_name": "somewhere",
                "location_address1": "over",
                "location_zip": "the",
                "location_city": "rainbow",
                "location_country": "FR",
                "description": "New description",
                "notify": "on",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # add organizer
        response = self.client.post(
            reverse("manage_event", kwargs={"pk": self.rsvped_event.pk}),
            data={"organizer": str(self.other_rsvp1.pk)},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_other_event(self):
        self.client.force_login(self.person.role)

        # manage_page
        response = self.client.get(
            reverse("manage_event", kwargs={"pk": self.other_event.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # get edit page
        response = self.client.get(
            reverse("edit_event", kwargs={"pk": self.other_event.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # post edit page
        response = self.client.post(
            reverse("edit_event", kwargs={"pk": self.other_event.pk}),
            data={
                "name": "New Name",
                "start_time": formats.localize_input(
                    timezone.now() + timezone.timedelta(hours=2), "%d/%m/%Y %H:%M"
                ),
                "end_time": formats.localize_input(
                    timezone.now() + timezone.timedelta(hours=4), "%d/%m/%Y %H:%M"
                ),
                "contact_name": "Arthur",
                "contact_email": "a@ziefzji.fr",
                "contact_phone": "06 06 06 06 06",
                "location_name": "somewhere",
                "location_address1": "over",
                "location_zip": "the",
                "location_city": "rainbow",
                "location_country": "FR",
                "description": "New description",
                "notify": "on",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # add organizer
        response = self.client.post(
            reverse("manage_event", kwargs={"pk": self.other_event.pk}),
            data={"organizer": str(self.other_rsvp2.pk)},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_create_event(self):
        self.client.force_login(self.person.role)

        res = self.client.get(reverse("create_event"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(
            path=reverse("perform_create_event"),
            data={
                "name": "Mon événement",
                "subtype": self.subtype.label,
                "start_time": formats.localize_input(
                    self.now + timezone.timedelta(days=1), "%d/%m/%Y %H:%M"
                ),
                "end_time": formats.localize_input(
                    self.now + timezone.timedelta(days=1, hours=1), "%d/%m/%Y %H:%M"
                ),
                "for_users": "I",
                "contact_name": "Moi",
                "contact_email": "moi@moi.fr",
                "contact_phone": "01 23 45 67 89",
                "contact_hide_phone": True,
                "location_name": "Chez moi",
                "location_address1": "123 rue truc",
                "location_address2": "",
                "location_city": "Paris",
                "location_zip": "75014",
                "location_country": "FR",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_cannot_create_too_long_event(self):
        self.client.force_login(self.person.role)

        res = self.client.post(
            path=reverse("perform_create_event"),
            data={
                "name": "Mon événement",
                "subtype": self.subtype.label,
                "start_time": formats.localize_input(
                    self.now + timezone.timedelta(days=1), "%d/%m/%Y %H:%M"
                ),
                "end_time": formats.localize_input(
                    self.now + timezone.timedelta(days=10, hours=1), "%d/%m/%Y %H:%M"
                ),
                "contact_name": "Moi",
                "contact_email": "moi@moi.fr",
                "contact_phone": "01 23 45 67 89",
                "contact_hide_phone": True,
                "location_name": "Chez moi",
                "location_address1": "123 rue truc",
                "location_address2": "",
                "location_city": "Paris",
                "location_zip": "75014",
                "location_country": "FR",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_edit_legal_fields(self):
        self.client.force_login(self.person.role)
        res = self.client.get(
            reverse("event_legal_form", args=[self.organized_event.pk])
        )

        self.assertContains(res, "Salle")
        self.assertNotContains(res, "Hébergement militant")

        self.client.post(
            reverse("event_legal_form", args=[self.organized_event.pk]),
            data={"salle": "gratuite", "salle_name": "Nom de la salle"},
        )
        self.organized_event.refresh_from_db()
        self.assertEqual(self.organized_event.legal["documents_salle"], "gratuite")
        self.assertEqual(
            self.organized_event.legal["documents_salle_name"], "Nom de la salle"
        )
        res = self.client.get(
            reverse("event_legal_form", args=[self.organized_event.pk])
        )
        self.assertContains(res, "Nom de la salle")

    def test_excluded_fields_are_not_in_form(self):
        self.subtype.config = {"excluded_fields": ["name"]}
        self.subtype.save()

        self.client.force_login(self.person.role)

        response = self.client.get(
            reverse("edit_event", kwargs={"pk": self.organized_event.pk})
        )

        self.assertNotContains(response, "Nom de l'événement")

        response = self.client.post(
            reverse("edit_event", kwargs={"pk": self.organized_event.pk}),
            data={
                "name": "New Name",
                "start_time": formats.localize_input(
                    self.now + timezone.timedelta(hours=2), "%d/%m/%Y %H:%M"
                ),
                "end_time": formats.localize_input(
                    self.now + timezone.timedelta(hours=4), "%d/%m/%Y %H:%M"
                ),
                "contact_name": "Arthur",
                "contact_email": "a@ziefzji.fr",
                "contact_phone": "06 06 06 06 06",
                "location_name": "somewhere",
                "location_address1": "over",
                "location_zip": "74928",
                "location_city": "rainbow",
                "location_country": "FR",
                "description": "New description",
                "notify": "on",
                "as_group": self.group.pk,
            },
        )

        # the form redirects to the event manage page on success
        self.assertRedirects(
            response, reverse("manage_event", kwargs={"pk": self.organized_event.pk})
        )

        self.organized_event.refresh_from_db()
        self.assertEqual(self.organized_event.name, "Organized event")

    @mock.patch("agir.events.views.event_views.send_event_report")
    def test_can_send_event_report_if_its_possible(self, send_event_report):
        """ Si les conditions sont réunies, on peut envoyer le résumé par mail.

        Les conditions sont : le mail n'a jamais été envoyé, l'événement est passé, le compte-rendu n'est pas vide."""
        self.client.force_login(self.person.role)
        session = self.client.session

        response = self.client.post(
            reverse("send_event_report", kwargs={"pk": self.past_event.pk})
        )
        self.assertRedirects(
            response, reverse("manage_event", kwargs={"pk": self.past_event.pk})
        )
        send_event_report.delay.assert_called_once()

        # # on simule le fait que le compte-rendu a bien été envoyé
        self.past_event.report_summary_sent = True
        self.past_event.save()
        response = self.client.get(
            reverse("manage_event", kwargs={"pk": self.past_event.pk})
        )
        self.assertContains(response, "Ce compte-rendu a déjà été envoyé")

    @mock.patch("agir.events.views.event_views.send_event_report")
    def test_report_is_sent_in_event_manage(self, send_event_report):
        """
        Test si le template affiche bien le fait que le compte-rendu à été envoyé la première fois que l'on retourne sur la page, mais pas les fois suivantes.
        """
        self.client.force_login(self.person.role)

        self.client.post(
            reverse("send_event_report", kwargs={"pk": self.past_event.pk})
        )

        response = self.client.get(
            reverse("manage_event", kwargs={"pk": self.past_event.pk})
        )
        # la tache `send event_report` n'est pas appeler. Mais une variable de session temporaire est utliser pour informer que le mail à été envoyé
        self.assertContains(response, "Ce compte-rendu a déjà été envoyé.")

        response = self.client.get(
            reverse("manage_event", kwargs={"pk": self.past_event.pk})
        )
        # la deuxième fois la variable de session n'existe plus
        self.assertNotContains(response, "Ce compte-rendu a déjà été envoyé")

    @mock.patch("agir.events.views.event_views.send_event_report")
    def test_can_not_send_event_report_when_nocondition(self, send_event_report):
        """ Si une des conditions manque, l'envoi du mail ne se fait pas.

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

    @mock.patch("django.db.transaction.on_commit")
    def test_attendees_notified_when_report_is_posted(self, on_commit):
        now = timezone.now()
        past_event = Event.objects.create(
            name="Evenement terminé",
            start_time=now - timedelta(days=1, hours=2),
            end_time=now - timedelta(days=1),
            subtype=self.subtype,
        )
        OrganizerConfig.objects.create(event=past_event, person=self.person)
        RSVP.objects.create(event=past_event, person=self.other_person)

        self.client.force_login(self.person.role)
        res = self.client.post(
            reverse("edit_event_report", args=[past_event.pk]),
            data={"report_content": "Un super compte-rendu de malade."},
        )
        self.assertRedirects(res, reverse("manage_event", args=[past_event.pk]))

        on_commit.assert_called_once()
        partial = on_commit.call_args[0][0]

        self.assertEqual(partial.func, notify_on_event_report.delay)
        self.assertEqual(partial.args, (past_event.pk,))


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
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
            payment_parameters={"price": 1000},
        )

        self.form_paying_event = Event.objects.create(
            name="Paying event",
            start_time=now + 3 * day,
            end_time=now + 3 * day + 4 * hour,
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

    @mock.patch("agir.events.actions.rsvps.send_rsvp_notification")
    def test_can_rsvp_to_simple_event_and_quit(self, rsvp_notification):
        self.client.force_login(self.person.role)

        # can see the form
        response = self.client.get(
            reverse("api_event_view", kwargs={"pk": self.simple_event.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["rsvp"])

        # can actually post the form
        response = self.client.post(
            reverse("rsvp_event", kwargs={"pk": self.simple_event.pk})
        )
        self.assertRedirects(
            response, reverse("view_event", kwargs={"pk": self.simple_event.pk})
        )
        self.assertIn(self.person, self.simple_event.attendees.all())
        self.assertEqual(2, self.simple_event.participants)

        rsvp_notification.delay.assert_called_once()

        rsvp = RSVP.objects.get(person=self.person, event=self.simple_event)
        self.assertEqual(rsvp_notification.delay.call_args[0][0], rsvp.pk)

        res = self.client.post(
            reverse("quit_event", kwargs={"pk": self.simple_event.pk})
        )
        self.assertRedirects(res, reverse("dashboard"))
        self.assertNotIn(self.person, self.simple_event.attendees.all())
        self.assertEqual(1, self.simple_event.participants)

    def test_can_view_rsvp(self):
        self.client.force_login(self.already_rsvped.role)

        url = reverse("api_event_view", kwargs={"pk": self.simple_event.pk})
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
        self.form_event.subscription_form.end_time = timezone.now() - timezone.timedelta(
            days=1
        )
        self.form_event.subscription_form.save()

        res = self.client.get(reverse("rsvp_event", kwargs={"pk": self.form_event.pk}))
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

        res = self.client.post(
            reverse("rsvp_event", kwargs={"pk": self.form_event.pk}),
            data={"custom-field": "another custom value"},
        )
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

    def test_cannot_rsvp_if_external(self):
        self.person.is_insoumise = False
        self.person.save()
        self.client.force_login(self.person.role)

        url = reverse("view_event", kwargs={"pk": self.simple_event.pk})

        # cannot see the form
        response = self.client.get(url)
        self.assertNotIn("Participer à cet événement", response.content.decode())

        # cannot actually post the form
        self.client.post(reverse("rsvp_event", kwargs={"pk": self.simple_event.pk}))
        self.assertNotIn(self.person, self.simple_event.attendees.all())

    def test_cannot_rsvp_if_form_is_yet_to_open(self):
        self.client.force_login(self.person.role)
        self.form_event.subscription_form.start_time = timezone.now() + timezone.timedelta(
            days=1
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
        self.now = now = timezone.now().astimezone(timezone.get_default_timezone())
        day = timezone.timedelta(days=1)
        hour = timezone.timedelta(hours=1)
        self.person = Person.objects.create_person("test@test.com", is_insoumise=False)
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
        self.assertEqual(Person.objects.get(email="test1@test.com").is_insoumise, False)


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

    def test_unlisted_events_are_not_in_dashboard_calendar(self):
        response = self.client.get(reverse("dashboard_old"))
        self.assertContains(response, "Un événement qui sera non listé")

        self.event.do_not_list = True
        self.event.save()

        response = self.client.get(reverse("dashboard_old"))
        self.assertNotContains(response, "Un événement qui sera non listé")
        pass

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
