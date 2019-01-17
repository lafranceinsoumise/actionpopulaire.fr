from django.test import TestCase

from agir.lib.tests.mixins import FakeDataMixin

from ..models import Person, PersonForm, PersonFormSubmission
from ..actions.person_forms import get_form_field_labels, get_formatted_submission
from ..actions.management import merge_persons


class PeopleFormActionsTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_person("person@corp.com")

        self.complex_form = PersonForm.objects.create(
            title="Formulaire complexe",
            slug="formulaire-complexe",
            description="Ma description complexe",
            confirmation_note="Ma note de fin",
            main_question="QUESTION PRINCIPALE",
            custom_fields=[
                {
                    "title": "Détails",
                    "fields": [
                        {
                            "id": "custom-field",
                            "type": "short_text",
                            "label": "Mon label",
                        },
                        {
                            "id": "custom-person-field",
                            "type": "short_text",
                            "label": "Prout",
                            "person_field": True,
                        },
                        {"id": "contact_phone", "person_field": True},
                        {
                            "id": "first_name",
                            "person_field": True,
                            "label": "SUPER PRENOM",
                        },
                        {
                            "id": "one-choice-field",
                            "type": "choice",
                            "label": "Choix",
                            "choices": [["A", "Le choix A"], ["B", "La réponse B"]],
                        },
                    ],
                }
            ],
        )

        self.submission1 = PersonFormSubmission.objects.create(
            person=self.person,
            form=self.complex_form,
            data={
                "custom-field": "saisie 1",
                "custom-person-field": "saisie 2",
                "contact_phone": "+33612345678",
                "first_name": "Truc",
                "one-choice-field": "B",
                "disappearing-field": "TUC",
            },
        )

    def test_get_form_field_labels(self):
        self.assertEqual(
            get_form_field_labels(self.complex_form),
            {
                "custom-field": "Mon label",
                "custom-person-field": "Prout",
                "contact_phone": Person._meta.get_field("contact_phone").verbose_name,
                "first_name": "SUPER PRENOM",
                "one-choice-field": "Choix",
            },
        )

    def test_get_formatted_submission(self):
        self.assertEqual(
            # disregard first three default fields
            get_formatted_submission(self.submission1, include_admin_fields=False),
            [
                {
                    "title": "Détails",
                    "data": [
                        {"label": "Mon label", "value": "saisie 1"},
                        {"label": "Prout", "value": "saisie 2"},
                        {
                            "label": Person._meta.get_field(
                                "contact_phone"
                            ).verbose_name,
                            "value": "+33612345678",
                        },
                        {"label": "SUPER PRENOM", "value": "Truc"},
                        {"label": "Choix", "value": "La réponse B"},
                    ],
                },
                {
                    "title": "Champs inconnus",
                    "data": [{"label": "disappearing-field", "value": "TUC"}],
                },
            ],
        )


class MergePeopleTestCase(FakeDataMixin, TestCase):
    def test_can_merge_people(self):
        u1, u2 = self.people["user1"], self.people["user2"]
        merge_persons(u1, u2)

        self.assertFalse(Person.objects.filter(pk=u2.pk).exists())
