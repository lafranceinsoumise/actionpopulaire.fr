from django.test import TestCase

from . import models


class ClientTestCase(TestCase):
    def test_can_create_client(self):
        client = models.Client.objects.create()
