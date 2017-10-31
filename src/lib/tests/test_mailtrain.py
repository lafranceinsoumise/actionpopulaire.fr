from unittest import mock

from django.test import TestCase

from lib import mailtrain
from people.models import Person


class MailTrainTestCase(TestCase):
    @mock.patch('lib.mailtrain.requests.post')
    def test_subscribe(self, request_post):
        mailtrain.subscribe('test@example.com')

        request_post.assert_called_once()
        self.assertEqual(request_post.call_args[1]['data']['EMAIL'], 'test@example.com')

    @mock.patch('lib.mailtrain.requests.post')
    def test_unsubscribe(self, request_post):
        mailtrain.unsubscribe('test@example.com')

        request_post.assert_called_once()
        self.assertEqual(request_post.call_args[1]['data']['EMAIL'], 'test@example.com')

    @mock.patch('lib.mailtrain.delete')
    @mock.patch('lib.mailtrain.subscribe')
    @mock.patch('lib.mailtrain.unsubscribe')
    def test_update_person(self, unsubscribe, subscribe, delete):
        person = Person.objects.create(email='email@example.com')

        mailtrain.update_person(person)
        subscribe.assert_called_once()

        person.subscribed = False
        person.save()
        mailtrain.update_person(person)
        unsubscribe.assert_called_once()
        subscribe.assert_called_once()

        person.add_email('email@bounced.com', bounced=True)
        person.set_primary_email('email@bounced.com')
        person.save()
        mailtrain.update_person(person)
        delete.assert_called_once()
        unsubscribe.assert_called_once()
        subscribe.assert_called_once()
