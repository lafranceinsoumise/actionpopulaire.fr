from unittest import mock

from django.test import TestCase, override_settings
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core import mail
from redislite import StrictRedis

from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from agir.authentication.models import Role
from agir.people.models import Person, PersonTag, PersonEmail, PersonForm, PersonFormSubmission
from agir.people.viewsets import LegacyPersonViewSet
from agir.people import tasks

from agir.events.models import Event, RSVP
from agir.groups.models import SupportGroup, Membership

from agir.lib.tests.mixins import FakeDataMixin


class PeopleTasksTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('me@me.org')

    def test_welcome_mail(self):
        tasks.send_welcome_mail(self.person.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])

    def test_unsubscribe_mail(self):
        tasks.send_unsubscribe_email(self.person.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].recipients(), [self.person.email])
