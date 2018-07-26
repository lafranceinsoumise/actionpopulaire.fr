from unittest import mock

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from agir.clients.models import Client
from agir.people.models import Person, PersonTag, PersonForm, PersonFormSubmission
from agir.lib.tests.mixins import FakeDataMixin


class DashboardTestCase(FakeDataMixin, TestCase):
    @mock.patch('agir.people.views.geocode_person')
    def test_contains_everything(self, geocode_person):
        self.client.force_login(self.data['people']['user2'].role)
        response = self.client.get(reverse('dashboard'))

        geocode_person.delay.assert_called_once()
        self.assertEqual(geocode_person.delay.call_args[0], (self.data['people']['user2'].pk, ))

        # own email
        self.assertContains(response, 'user2@example.com')
        # managed group
        self.assertContains(response, self.data['groups']['user2_group'].name)
        # member groups
        self.assertContains(response, self.data['groups']['user1_group'].name)
        # next events
        self.assertContains(response, self.data['events']['user1_event1'].name)
        # events of group
        self.assertContains(response, self.data['events']['user1_event2'].name)


class MessagePreferencesTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')
        self.person.add_email('test2@test.com')
        self.client.force_login(self.person.role)

    def test_can_load_message_preferences_page(self):
        res = self.client.get('/message_preferences/')

        # should show the current email address
        self.assertContains(res, 'test@test.com')
        self.assertContains(res, 'test2@test.com')

    def test_can_see_email_management(self):
        res = self.client.get('/message_preferences/adresses/')

        # should show the current email address
        self.assertContains(res, 'test@test.com')
        self.assertContains(res, 'test2@test.com')

    def test_can_add_delete_address(self):
        emails = list(self.person.emails.all())

        # should be possible to get the delete page for one of the two addresses, and to actually delete
        res = self.client.get('/message_preferences/adresses/{}/supprimer/'.format(emails[1].pk))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post('/message_preferences/adresses/{}/supprimer/'.format(emails[1].pk))
        self.assertRedirects(res, reverse('email_management'))

        # address should indeed be gone
        self.assertEqual(len(self.person.emails.all()), 1)
        self.assertEqual(self.person.emails.first(), emails[0])

        # both get and post should give 403 when there is only one primary address
        res = self.client.get('/message_preferences/adresses/{}/supprimer/'.format(emails[0].pk))
        self.assertRedirects(res, reverse('email_management'))

        res = self.client.post('/message_preferences/adresses/{}/supprimer/'.format(emails[0].pk))
        self.assertRedirects(res, reverse('email_management'))
        self.assertEqual(len(self.person.emails.all()), 1)

    def test_can_add_address(self):
        res = self.client.post('/message_preferences/adresses/', data={'address': 'test3@test.com'})
        self.assertRedirects(res, '/message_preferences/adresses/')

        res = self.client.post('/message_preferences/adresses/', data={'address': 'TeST4@TeSt.COM'})
        self.assertRedirects(res, '/message_preferences/adresses/')

        self.assertCountEqual(
            [e.address for e in self.person.emails.all()],
            ['test@test.com', 'test2@test.com', 'test3@test.com', 'test4@test.com']
        )

    def test_can_stop_messages(self):
        res = self.client.post('/message_preferences/', data={
            'no_mail': True,
            'gender': '',
            'primary_email': self.person.emails.first().id
        })
        self.assertEqual(res.status_code, 302)
        self.person.refresh_from_db()
        self.assertEqual(self.person.subscribed, False)
        self.assertEqual(self.person.event_notifications, False)
        self.assertEqual(self.person.group_notifications, False)
        self.assertEqual(self.person.draw_participation, False)


class ProfileFormTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            'test@test.com'
        )

    def test_can_add_tag(self):
        self.client.force_login(self.person.role)
        response = self.client.post(reverse('change_profile'), {'info blogueur': 'on'})

        self.assertEqual(response.status_code, 302)
        self.assertIn('info blogueur', [tag.label for tag in self.person.tags.all()])

    @mock.patch('agir.people.forms.geocode_person')
    def test_can_change_address(self, geocode_person):
        self.client.force_login(self.person.role)

        address_fields = {
            'location_address1': '73 boulevard Arago',
            'location_zip': '75013',
            'location_country': 'FR',
            'location_city': 'Paris',
        }

        response = self.client.post(reverse('change_profile'), address_fields)

        geocode_person.delay.assert_called_once()
        self.assertEqual(geocode_person.delay.call_args[0], (self.person.pk,))

        geocode_person.reset_mock()
        response = self.client.post(reverse('change_profile'), {
            'first_name': 'Arthur',
            'last_name': 'Cheysson',
            **address_fields
        })
        geocode_person.delay.assert_not_called()


class UnsubscribeFormTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('test@test.com')

    @mock.patch("agir.people.forms.send_unsubscribe_email")
    def test_can_post(self, patched_send_unsubscribe_email):
        response = self.client.post(reverse('unsubscribe'), {'email': 'test@test.com'})

        self.person.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.person.subscribed, False)
        self.assertEqual(self.person.event_notifications, False)
        self.assertEqual(self.person.group_notifications, False)
        patched_send_unsubscribe_email.delay.assert_called_once()
        self.assertEqual(patched_send_unsubscribe_email.delay.call_args[0], (self.person.pk,))


class DeleteFormTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('delete@delete.com')

    def test_can_delete_account(self):
        self.client.force_login(self.person.role)

        response = self.client.post(reverse('delete_account'))
        self.assertEqual(response.status_code, 302)
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(pk=self.person.pk)


class SimpleSubscriptionFormTestCase(TestCase):
    @mock.patch("agir.people.forms.send_welcome_mail")
    def test_can_post(self, patched_send_welcome_mail):
        response = self.client.post('/inscription/', {'email': 'example@example.com', 'location_zip': '75018'})

        self.assertEqual(response.status_code, 302)
        person = Person.objects.get_by_natural_key('example@example.com')

        patched_send_welcome_mail.delay.assert_called_once()
        self.assertEqual(patched_send_welcome_mail.delay.call_args[0][0], person.pk)


class OverseasSubscriptionTestCase(TestCase):
    @mock.patch("agir.people.forms.send_welcome_mail")
    def test_can_post(self, patched_send_welcome_mail):
        response = self.client.post('/inscription/etranger/', {
            'email': 'example@example.com',
            'location_address1': '1 ZolaStraße',
            'location_zip': '10178',
            'location_city': 'Berlin',
            'location_country': 'DE'
        })

        self.assertEqual(response.status_code, 302)
        person = Person.objects.get_by_natural_key('example@example.com')
        self.assertEqual(person.location_city, 'Berlin')

        patched_send_welcome_mail.delay.assert_called_once()
        self.assertEqual(patched_send_welcome_mail.delay.call_args[0][0], person.pk)


class PersonFormTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('person@corp.com')
        self.person.meta['custom-person-field'] = 'Valeur méta préexistante'
        self.person.save()
        self.tag1 = PersonTag.objects.create(label='tag1', description='Description TAG1')
        self.tag2 = PersonTag.objects.create(label='tag2', description='Description TAG2')

        self.single_tag_form = PersonForm.objects.create(
            title='Formulaire simple',
            slug='formulaire-simple',
            description='Ma description simple',
            confirmation_note='Ma note de fin',
            main_question='QUESTION PRINCIPALE',
            send_answers_to='test@example.com',
            send_confirmation=True,
            custom_fields=[{
                'title': 'Profil',
                'fields': [{
                    'id': 'contact_phone',
                    'person_field': True
                }]
            }],
        )
        self.single_tag_form.tags.add(self.tag1)

        self.complex_form = PersonForm.objects.create(
            title='Formulaire complexe',
            slug='formulaire-complexe',
            description='Ma description complexe',
            confirmation_note='Ma note de fin',
            main_question='QUESTION PRINCIPALE',
            custom_fields=[{
                'title': 'Détails',
                'fields': [
                    {
                        'id': 'custom-field',
                        'type': 'short_text',
                        'label': 'Mon label'
                    },
                    {
                        'id': 'custom-person-field',
                        'type': 'short_text',
                        'label': 'Prout',
                        'person_field': True
                    },
                    {
                        'id': 'contact_phone',
                        'person_field': True
                    }
                ]
            }]
        )
        self.complex_form.tags.add(self.tag1)
        self.complex_form.tags.add(self.tag2)

        self.client.force_login(self.person.role)

    def test_flatten_fields_property(self):
        self.assertEqual(self.complex_form.fields_dict, {
             'custom-field': {
                 'id': 'custom-field',
                 'type': 'short_text',
                 'label': 'Mon label'
             },
             'custom-person-field': {
                 'id': 'custom-person-field',
                 'type': 'short_text',
                 'label': 'Prout',
                 'person_field': True
             },
             'contact_phone': {
                 'id': 'contact_phone',
                 'person_field': True
             }
        })

    def test_title_and_description(self):
        res = self.client.get('/formulaires/formulaire-simple/')

        # Contient le titre et la description
        self.assertContains(res, self.single_tag_form.title)
        self.assertContains(res, self.single_tag_form.description)

        res = self.client.get('/formulaires/formulaire-simple/confirmation/')
        self.assertContains(res, self.single_tag_form.title)
        self.assertContains(res, self.single_tag_form.confirmation_note)

    @mock.patch('agir.people.tasks.send_person_form_confirmation')
    @mock.patch('agir.people.tasks.send_person_form_notification')
    def test_can_validate_simple_form(self, send_confirmation, send_notification):
        res = self.client.get('/formulaires/formulaire-simple/')

        # contains phone number field
        self.assertContains(res, 'contact_phone')

        # check contact phone is compulsory
        res = self.client.post('/formulaires/formulaire-simple/', data={})
        self.assertContains(res, 'has-error')

        # check can validate
        res = self.client.post('/formulaires/formulaire-simple/', data={'contact_phone': '06 04 03 02 04'})
        self.assertRedirects(res, '/formulaires/formulaire-simple/confirmation/')

        # check user has been well modified
        self.person.refresh_from_db()

        self.assertEqual(self.person.contact_phone, '+33604030204')
        self.assertIn(self.tag1, self.person.tags.all())

        submissions = PersonFormSubmission.objects.all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0].data['contact_phone'], '+33604030204')

        send_confirmation.delay.assert_called_once()
        send_notification.delay.assert_called_once()

    def test_can_validate_complex_form(self):
        res = self.client.get('/formulaires/formulaire-complexe/')

        self.assertContains(res, 'contact_phone')
        self.assertContains(res, 'custom-field')
        self.assertContains(res, 'Valeur méta préexistante')

        # assert tag is compulsory
        res = self.client.post('/formulaires/formulaire-complexe/', data={
            'contact_phone': '06 34 56 78 90',
            'custom-field': 'Mon super champ texte libre'
        })
        self.assertContains(res, 'has-error')

        res = self.client.post('/formulaires/formulaire-complexe/', data={
            'tag': 'tag2',
            'contact_phone': '06 34 56 78 90',
            'custom-field': 'Mon super champ texte libre',
            'custom-person-field': 'Mon super champ texte libre à mettre dans Person.metas'
        })
        self.assertRedirects(res, '/formulaires/formulaire-complexe/confirmation/')

        self.person.refresh_from_db()

        self.assertCountEqual(self.person.tags.all(), [self.tag2])
        self.assertEqual(self.person.meta['custom-person-field'], 'Mon super champ texte libre à mettre dans Person.metas')

        submissions = PersonFormSubmission.objects.all()
        self.assertEqual(len(submissions), 1)

        self.assertEqual(submissions[0].data['custom-field'], 'Mon super champ texte libre')
        self.assertEqual(submissions[0].data['custom-person-field'], 'Mon super champ texte libre à mettre dans Person.metas')

    def test_cannot_view_closed_forms(self):
        self.complex_form.end_time = timezone.now() - timezone.timedelta(days=1)
        self.complex_form.save()

        res = self.client.get('/formulaires/formulaire-complexe/')
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

    def test_cannot_post_on_closed_forms(self):
        self.complex_form.end_time = timezone.now() - timezone.timedelta(days=1)
        self.complex_form.save()

        res = self.client.post('/formulaires/formulaire-complexe/', data={
            'tag': 'tag2',
            'contact_phone': '06 34 56 78 90',
            'custom-field': 'Mon super champ texte libre',
            'custom-person-field': 'Mon super champ texte libre à mettre dans Person.metas'
        })
        self.assertContains(res, "Ce formulaire est maintenant fermé.")


class SearchPersonTestCase(FakeDataMixin, APITestCase):
    def setUp(self):
        super().setUp()

        self.url = reverse('search_person')

        self.view_permission_client = Client.objects.create_client('client')
        content_type = ContentType.objects.get_for_model(Person)
        permission = Permission.objects.get(codename='view_person', content_type=content_type)

        self.view_permission_client.role.user_permissions.add(permission)

    def test_cannot_search_when_not_logged_in(self):
        res = self.client.get(self.url, {'address': 'user1@example.com'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_search_without_permission(self):
        self.client.force_login(self.people['user1'].role)

        res = self.client.get(self.url, {'address': 'user1@example.com'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_search_with_proper_permission(self):
        self.client.force_login(self.view_permission_client.role)

        res = self.client.get(self.url, {'address': 'user1@example.com'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(res.data['email'], 'user1@example.com')

    def test_can_search_with_any_capitalization(self):
        self.client.force_login(self.view_permission_client.role)

        res = self.client.get(self.url, {'address': 'UsEr1@exAMple.com'})
        self.assertEqual(res.data['email'], 'user1@example.com')
