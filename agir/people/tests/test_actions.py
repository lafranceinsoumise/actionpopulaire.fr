import json
from unittest import skip, mock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db import IntegrityError, transaction
from django.utils import timezone, formats
from django.utils.http import urlquote_plus
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core import mail

from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework.reverse import reverse
from rest_framework import status

from ..models import Person, PersonTag, PersonEmail, PersonForm, PersonFormSubmission
from .. import tasks
from ..actions.person_forms import get_form_field_labels, get_formatted_submission


class PeopleFormActionsTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person('person@corp.com')

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
                    },
                    {
                        'id': 'first_name',
                        'person_field': True,
                        'label': 'SUPER PRENOM'
                    },
                    {
                        'id': 'one-choice-field',
                        'type': 'choice',
                        'label': 'Choix',
                        'choices': [
                            ['A', 'Le choix A'],
                            ['B', 'La réponse B']
                        ]
                    }
                ]
            }]
        )

        self.submission1 = PersonFormSubmission.objects.create(
            person=self.person,
            form=self.complex_form,
            data={
                'custom-field': 'saisie 1',
                'custom-person-field': 'saisie 2',
                'contact_phone': '+33612345678',
                'first_name': 'Truc',
                'one-choice-field': 'B',
                'disappearing-field': 'TUC'
            }
        )

    def test_get_form_field_labels(self):
        self.assertEqual(
            get_form_field_labels(self.complex_form),
            {
                'custom-field': 'Mon label', 'custom-person-field': 'Prout',
                'contact_phone': Person._meta.get_field('contact_phone').verbose_name,
                'first_name': 'SUPER PRENOM',
                'one-choice-field': 'Choix'
            }
        )

    def test_get_formatted_submission(self):
        self.assertEqual(
            get_formatted_submission(self.submission1),
            [
                {'label': 'Mon label', 'value': 'saisie 1'},
                {'label': 'Prout', 'value': 'saisie 2'},
                {'label': Person._meta.get_field('contact_phone').verbose_name, 'value': '+33612345678'},
                {'label': 'SUPER PRENOM', 'value': 'Truc'},
                {'label': 'Choix', 'value': 'La réponse B'},
                {'label': 'disappearing-field', 'value': 'TUC'},
            ]
        )
