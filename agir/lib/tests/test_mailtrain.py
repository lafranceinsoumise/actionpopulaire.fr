from unittest import mock

from django.test import TestCase, override_settings

from agir.lib import mailtrain
from agir.people.models import Person

@override_settings(MAILTRAIN_DISABLE=False)
class MailTrainTestCase(TestCase):
    @mock.patch('agir.lib.mailtrain.s.post')
    def test_subscribe(self, request_post):
        mailtrain.subscribe('test@example.com')

        request_post.assert_called_once()
        self.assertEqual(request_post.call_args[1]['data']['EMAIL'], 'test@example.com')

    @mock.patch('agir.lib.mailtrain.s.post')
    def test_unsubscribe(self, request_post):
        mailtrain.unsubscribe('test@example.com')

        request_post.assert_called_once()
        self.assertEqual(request_post.call_args[1]['data']['EMAIL'], 'test@example.com')

    @mock.patch('agir.people.tasks.update_mailtrain')
    @mock.patch('agir.lib.mailtrain.delete')
    @mock.patch('agir.lib.mailtrain.subscribe')
    @mock.patch('agir.lib.mailtrain.unsubscribe')
    def test_update_person(self, unsubscribe, subscribe, delete, *args):
        person = Person.objects.create(email='email@example.com')

        mailtrain.update_person(person)
        subscribe.assert_called_once()

        person.subscribed = False
        person.save()
        mailtrain.update_person(person)
        unsubscribe.assert_called_once()
        subscribe.assert_called_once()

        person.add_email('second@domain.com')
        person.primary_email.bounced = True
        person.primary_email.save()
        person.subscribed = True
        person.save()
        mailtrain.update_person(person)
        delete.assert_called_once()
        unsubscribe.assert_called_once()
        self.assertEqual(subscribe.call_count, 2)
