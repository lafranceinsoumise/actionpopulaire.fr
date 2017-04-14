import uuid
from datetime import datetime

from django.test import TestCase
from django.db import IntegrityError

from . import models


class UUIDIdentifiedMixinTestCase(TestCase):
    def test_auto_create_uuid(self):
        instance = models.UUIDModel.objects.create()

        self.assertIsInstance(instance.id, uuid.UUID)
        self.assertEqual(instance.id.version, 4)

    def test_uuid_is_pk(self):
        instance = models.UUIDModel.objects.create()

        self.assertEqual(instance.id, instance.pk)
        self.assertEqual(instance, models.UUIDModel.objects.get(pk=instance.pk))

    def test_different_uuids(self):
        instance1 = models.UUIDModel.objects.create()
        instance2 = models.UUIDModel.objects.create()

        self.assertNotEqual(instance1.pk, instance2.pk)


class NationBuilderIdTestCase(TestCase):
    def test_can_create_no_nb_id(self):
        instance1 = models.NBModel.objects.create()
        instance2 = models.NBModel.objects.create()

        self.assertIsNone(instance1.nb_id)
        self.assertIsNone(instance2.nb_id)

    def test_nb_id_enforced_unique(self):
        models.NBModel.objects.create(nb_id=1)

        with self.assertRaises(IntegrityError):
            models.NBModel.objects.create(nb_id=1)


class APIResourceTestCase(TestCase):
    def test_has_uuid(self):
        instance = models.APIResource.objects.create()

        self.assertIsInstance(instance.pk, uuid.UUID)

    def test_has_timestamps(self):
        instance = models.APIResource.objects.create()

        self.assertIsInstance(instance.created, datetime)
        self.assertIsInstance(instance.modified, datetime)

    def test_timestamp_semantics(self):
        instance = models.APIResource.objects.create()
        original_created, original_modified = instance.created, instance.modified

        self.assertGreaterEqual(original_modified, original_created)

        # save and check modified changed
        instance.save()
        self.assertGreater(instance.modified, original_modified)


class LabelTestCase(TestCase):
    def test_has_name(self):
        instance = models.Label.objects.create(label='label')

        self.assertEqual(instance.label, 'label')

    def test_unique_labels(self):
        models.Label.objects.create(label='label')

        with self.assertRaises(IntegrityError):
            models.Label.objects.create(label='label')

    def test_can_get_by_label(self):
        instance = models.Label.objects.create(label='label')

        self.assertEqual(instance, models.Label.objects.get_by_natural_key('label'))

    def test_str_is_label(self):
        instance = models.Label.objects.create(label='label')

        self.assertEqual(str(instance), 'label')
