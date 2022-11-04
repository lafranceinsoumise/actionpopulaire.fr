from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from nuntius.models import Campaign

from agir.api.redis import using_separate_redis_server
from agir.people.person_forms.actions import get_people_form_class
from agir.people.person_forms.display import default_person_form_display
from agir.people.models import Person, PersonTag, PersonForm, PersonFormSubmission


class SetUpPersonFormsMixin:
    def setUp(self):
        self.person = Person.objects.create_insoumise(
            "person@corp.com", create_role=True
        )
        self.person.meta["custom-person-field"] = "Valeur méta préexistante"
        self.person.save()
        self.tag1 = PersonTag.objects.create(
            label="tag1", description="Description TAG1"
        )
        self.tag2 = PersonTag.objects.create(
            label="tag2", description="Description TAG2"
        )

        self.single_tag_form = PersonForm.objects.create(
            title="Formulaire simple",
            slug="formulaire-simple",
            description="Ma description simple",
            confirmation_note="Ma note de fin",
            main_question="QUESTION PRINCIPALE",
            send_answers_to="test@example.com",
            send_confirmation=True,
            custom_fields=[
                {
                    "title": "Profil",
                    "fields": [{"id": "contact_phone", "person_field": True}],
                }
            ],
        )
        self.single_tag_form.tags.add(self.tag1)

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
                            "editable": True,
                        },
                        {
                            "id": "custom-person-field",
                            "type": "short_text",
                            "label": "Prout",
                            "person_field": True,
                            "editable": True,
                        },
                        {"id": "contact_phone", "person_field": True, "editable": True},
                    ],
                }
            ],
        )
        self.complex_form.tags.add(self.tag1)
        self.complex_form.tags.add(self.tag2)

        self.client.force_login(self.person.role)


class ViewPersonFormTestCase(SetUpPersonFormsMixin, TestCase):
    def test_flatten_fields_property(self):
        self.assertEqual(
            self.complex_form.fields_dict,
            {
                "custom-field": {
                    "id": "custom-field",
                    "type": "short_text",
                    "label": "Mon label",
                    "editable": True,
                },
                "custom-person-field": {
                    "id": "custom-person-field",
                    "type": "short_text",
                    "label": "Prout",
                    "person_field": True,
                    "editable": True,
                },
                "contact_phone": {
                    "id": "contact_phone",
                    "person_field": True,
                    "editable": True,
                },
            },
        )

    def test_title_and_description(self):
        res = self.client.get("/formulaires/formulaire-simple/")

        # Contient le titre et la description
        self.assertContains(res, self.single_tag_form.title)
        self.assertContains(res, self.single_tag_form.description)

        res = self.client.get("/formulaires/formulaire-simple/confirmation/")
        self.assertContains(res, self.single_tag_form.title)
        self.assertContains(res, self.single_tag_form.confirmation_note)

    @mock.patch("agir.people.tasks.send_person_form_confirmation")
    @mock.patch("agir.people.tasks.send_person_form_notification")
    def test_can_validate_simple_form(self, send_confirmation, send_notification):
        res = self.client.get("/formulaires/formulaire-simple/")

        # contains phone number field
        self.assertContains(res, "contact_phone")

        # check contact phone is compulsory
        res = self.client.post("/formulaires/formulaire-simple/", data={})
        self.assertContains(res, "has-error")

        # check can validate
        res = self.client.post(
            "/formulaires/formulaire-simple/", data={"contact_phone": "06 04 03 02 04"}
        )
        self.assertRedirects(res, "/formulaires/formulaire-simple/confirmation/")

        # check user has been well modified
        self.person.refresh_from_db()

        self.assertEqual(self.person.contact_phone, "+33604030204")
        self.assertIn(self.tag1, self.person.tags.all())

        submissions = PersonFormSubmission.objects.all()
        self.assertEqual(len(submissions), 1)
        self.assertEqual(submissions[0].data["contact_phone"], "+33604030204")

        send_confirmation.delay.assert_called_once()
        send_notification.delay.assert_called_once()

    def test_anonymous_form_does_not_create_person(self):
        self.client.logout()

        self.single_tag_form.allow_anonymous = True
        self.single_tag_form.save()

        res = self.client.get("/formulaires/formulaire-simple/")

        res = self.client.post(
            "/formulaires/formulaire-simple/", data={"contact_phone": "06 04 03 02 04"}
        )
        self.assertRedirects(res, "/formulaires/formulaire-simple/confirmation/")

        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(contact_phone="+33604030204")

    def test_can_validate_complex_form(self):
        res = self.client.get("/formulaires/formulaire-complexe/")

        self.assertContains(res, "contact_phone")
        self.assertContains(res, "custom-field")
        self.assertContains(res, "Valeur méta préexistante")

        # assert tag is compulsory
        res = self.client.post(
            "/formulaires/formulaire-complexe/",
            data={
                "contact_phone": "06 34 56 78 90",
                "custom-field": "valeur du champ libre person_field false",
            },
        )
        self.assertContains(res, "has-error")

        res = self.client.post(
            "/formulaires/formulaire-complexe/",
            data={
                "tag": "tag2",
                "contact_phone": "06 34 56 78 90",
                "custom-field": "valeur du champ libre person_field false",
                "custom-person-field": "valeur du champ libre avec person_field true",
            },
        )
        self.assertRedirects(res, "/formulaires/formulaire-complexe/confirmation/")

        self.person.refresh_from_db()

        self.assertCountEqual(self.person.tags.all(), [self.tag2])
        self.assertEqual(
            self.person.meta["custom-person-field"],
            "valeur du champ libre avec person_field true",
        )

        submissions = PersonFormSubmission.objects.all()
        self.assertEqual(len(submissions), 1)

        self.assertEqual(
            submissions[0].data["custom-field"],
            "valeur du champ libre person_field false",
        )
        self.assertEqual(
            submissions[0].data["custom-person-field"],
            "valeur du champ libre avec person_field true",
        )

    def test_can_update_form(self):
        self.complex_form.editable = True
        self.complex_form.save()
        self.test_can_validate_complex_form()

        self.assertEqual(PersonFormSubmission.objects.count(), 1)
        edit_url = reverse(
            "edit_person_form_submission",
            args=[self.complex_form.slug, PersonFormSubmission.objects.get().pk],
        )

        res = self.client.get(
            reverse("view_person_form", args=[self.complex_form.slug])
        )
        self.assertRedirects(res, edit_url)

        res = self.client.get(edit_url)
        self.assertContains(
            res, "valeur du champ libre person_field false"
        )  # data from first post is present

        res = self.client.post(
            edit_url,
            data={
                "tag": "tag1",
                "contact_phone": "06 34 56 78 91",
                "custom-field": "valeur modifié du champ libre person_field false",
                "custom-person-field": "valeur modifiée du champ libre person_field true",
            },
        )
        self.assertRedirects(res, "/formulaires/formulaire-complexe/confirmation/")

        self.person.refresh_from_db()

        self.assertCountEqual(self.person.tags.all(), [self.tag1, self.tag2])
        self.assertEqual(
            self.person.meta["custom-person-field"],
            "valeur modifiée du champ libre person_field true",
        )

        self.assertEqual(PersonFormSubmission.objects.count(), 1)

        submission = PersonFormSubmission.objects.get()
        self.assertEqual(
            submission.data["custom-field"],
            "valeur modifié du champ libre person_field false",
        )
        self.assertEqual(
            submission.data["custom-person-field"],
            "valeur modifiée du champ libre person_field true",
        )

    def test_only_update_allowed_fields(self):
        self.complex_form.editable = True
        self.complex_form.fields_dict["custom-person-field"]["editable"] = False
        self.complex_form.save()
        self.test_can_validate_complex_form()

        edit_url = reverse(
            "edit_person_form_submission",
            args=[self.complex_form.slug, PersonFormSubmission.objects.get().pk],
        )

        self.client.post(
            edit_url,
            data={
                "tag": "tag1",
                "contact_phone": "06 34 56 78 91",
                "custom-field": "valeur modifié du champ libre person_field false",
                "custom-person-field": "valeur modifiée du champ libre person_field true",
            },
        )

        self.person.refresh_from_db()

        self.assertCountEqual(self.person.tags.all(), [self.tag2, self.tag1])
        self.assertEqual(
            self.person.meta["custom-person-field"],
            "valeur du champ libre avec person_field true",
        )

        submissions = PersonFormSubmission.objects.all()
        self.assertEqual(len(submissions), 1)

        self.assertEqual(
            submissions[0].data["custom-field"],
            "valeur modifié du champ libre person_field false",
        )
        self.assertEqual(
            submissions[0].data["custom-person-field"],
            "valeur du champ libre avec person_field true",
        )

    def test_creates_new_submission_if_not_editable(self):
        self.test_can_validate_complex_form()

        res = self.client.get(
            reverse("view_person_form", args=[self.complex_form.slug])
        )
        self.assertNotContains(
            res, "valeur du champ libre person_field false"
        )  # data from first post must not be present
        self.client.post(
            reverse("view_person_form", args=[self.complex_form.slug]),
            data={
                "tag": "tag1",
                "contact_phone": "06 34 56 78 91",
                "custom-field": "valeur modifié du champ libre person_field false",
                "custom-person-field": "valeur modifiée du champ libre person_field true",
            },
        )
        submissions = PersonFormSubmission.objects.all()
        self.assertEqual(len(submissions), 2)

    def test_person_newsletters_field_add_without_overriding(self):
        self.person.newsletters = [Person.NEWSLETTER_2022]
        self.person.save()
        PersonForm.objects.create(
            title="Newsletters",
            slug="newsletters",
            description="Accepter les newsletters",
            confirmation_note="Acceptées !",
            main_question="Alors ?",
            custom_fields=[
                {
                    "title": "Newsletters",
                    "fields": [
                        {
                            "id": "newsletters",
                            "type": "newsletters",
                            "label": "Acceptez-vous ?",
                            "person_field": True,
                        }
                    ],
                }
            ],
        )
        res = self.client.get("/formulaires/newsletters/")
        self.assertContains(res, "newsletters")
        self.assertNotIn(Person.NEWSLETTER_2022_LIAISON, self.person.newsletters)
        self.assertIn(Person.NEWSLETTER_2022, self.person.newsletters)
        res = self.client.post(
            "/formulaires/newsletters/",
            data={},
        )
        self.assertContains(res, "has-error")
        res = self.client.post(
            "/formulaires/newsletters/",
            data={"newsletters": [Person.NEWSLETTER_2022_LIAISON]},
        )
        self.assertRedirects(res, "/formulaires/newsletters/confirmation/")
        self.person.refresh_from_db()
        self.assertIn(Person.NEWSLETTER_2022_LIAISON, self.person.newsletters)
        self.assertIn(Person.NEWSLETTER_2022, self.person.newsletters)


class AccessControlTestCase(SetUpPersonFormsMixin, TestCase):
    def test_cannot_access_not_anonymous_form(self):
        self.client.logout()

        res = self.client.get("/formulaires/formulaire-simple/")

        self.assertRedirects(
            res, reverse("short_code_login") + "?next=/formulaires/formulaire-simple/"
        )

    def test_cannot_view_closed_forms(self):
        self.complex_form.end_time = timezone.now() - timezone.timedelta(days=1)
        self.complex_form.save()

        res = self.client.get("/formulaires/formulaire-complexe/")
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

    def test_cannot_post_on_closed_forms(self):
        self.complex_form.end_time = timezone.now() - timezone.timedelta(days=1)
        self.complex_form.save()

        res = self.client.post(
            "/formulaires/formulaire-complexe/",
            data={
                "tag": "tag2",
                "contact_phone": "06 34 56 78 90",
                "custom-field": "valeur du champ libre person_field false",
                "custom-person-field": "valeur du champ libre avec person_field true",
            },
        )
        self.assertContains(res, "Ce formulaire est maintenant fermé.")

    def test_cannot_view_yet_to_open_forms(self):
        self.complex_form.start_time = timezone.now() + timezone.timedelta(days=1)
        self.complex_form.before_message = "SENTINEL"
        self.complex_form.save()

        res = self.client.get("/formulaires/formulaire-complexe/")
        self.assertContains(res, "SENTINEL")

    def test_cannot_post_on_yet_to_open_forms(self):
        self.complex_form.start_time = timezone.now() + timezone.timedelta(days=1)
        self.complex_form.before_message = "SENTINEL"
        self.complex_form.save()

        res = self.client.post(
            "/formulaires/formulaire-complexe/",
            data={
                "tag": "tag2",
                "contact_phone": "06 34 56 78 90",
                "custom-field": "valeur du champ libre person_field false",
                "custom-person-field": "valeur du champ libre avec person_field true",
            },
        )
        self.assertContains(res, "SENTINEL")

    def test_can_access_restricted_form_with_tag(self):
        self.single_tag_form.required_tags.add(self.tag2)
        self.single_tag_form.unauthorized_message = "SENTINEL"
        self.single_tag_form.save()
        self.person.tags.add(self.tag2)

        res = self.client.get("/formulaires/formulaire-simple/")
        self.assertNotContains(res, "SENTINEL")

        res = self.client.post(
            "/formulaires/formulaire-simple/", {"contact_phone": "06 23 45 67 89"}
        )
        self.assertRedirects(res, "/formulaires/formulaire-simple/confirmation/")

    def test_cannot_access_restricted_form_without_tag(self):
        self.single_tag_form.required_tags.add(self.tag2)
        self.single_tag_form.unauthorized_message = "SENTINEL"
        self.single_tag_form.save()

        res = self.client.get("/formulaires/formulaire-simple/")
        self.assertContains(res, "SENTINEL")

        res = self.client.post(
            "/formulaires/formulaire-simple/", {"contact_phone": "06 23 45 67 89"}
        )
        self.assertEqual(res.status_code, 200)


class SubmissionFormatTestCase(TestCase):
    def setUp(self):
        self.person = Person.objects.create_insoumise("person@corp.com")
        self.form = PersonForm.objects.create(
            title="Formulaire",
            slug="formulaire",
            description="Ma description simple",
            confirmation_note="Ma note de fin",
            custom_fields=[
                {
                    "title": "Une partie",
                    "fields": [
                        {"id": "first_name", "person_field": True},
                        {"id": "date", "type": "datetime", "label": "Date"},
                        {"id": "phone_number", "type": "phone_number", "label": "Tel."},
                        {"id": "file", "type": "file", "label": "Fichier"},
                    ],
                }
            ],
        )

        self.some_date = timezone.make_aware(timezone.datetime(2050, 5, 2))

        self.submission = PersonFormSubmission.objects.create(
            form=self.form,
            person=self.person,
            data={
                "first_name": "Arthur",
                "date": self.some_date,
                "phone_number": "+33612345678",
                "file": "test/truc.pdf",
                "missing_field": "Unknown value",
            },
        )
        self.submission.refresh_from_db()

    def test_display_single_formatting(self):
        formatted_submission = default_person_form_display.get_formatted_submission(
            self.submission
        )

        self.assertEqual(
            formatted_submission,
            [
                {
                    "title": "Une partie",
                    "data": [
                        {"label": "Prénom", "value": "Arthur"},
                        {"label": "Date", "value": "2 mai 2050 00:00"},
                        {"label": "Tel.", "value": "+33 6 12 34 56 78"},
                        {
                            "label": "Fichier",
                            "value": f'<a href="test/truc.pdf">Fichier 1</a>',
                        },
                    ],
                },
                {
                    "title": "Champs inconnus",
                    "data": [{"label": "missing_field", "value": "Unknown value"}],
                },
            ],
        )

    def test_get_form_labels(self):
        labels = default_person_form_display.get_form_field_labels(self.form)

        self.assertEqual(
            labels,
            {
                "first_name": "Prénom",
                "date": "Date",
                "phone_number": "Tel.",
                "file": "Fichier",
            },
        )


class FieldsTestCase(TestCase):
    def setUp(self) -> None:
        self.person = Person.objects.create_insoumise(
            "test@example.com", create_role=True
        )
        self.other_person = Person.objects.create_insoumise("test2@example.com")

    # utilise un token bucket
    @using_separate_redis_server
    def test_person_choice_field_allow_self(self):
        person_form = PersonForm.objects.create(
            title="Formulaire",
            slug="formulaire",
            description="description",
            confirmation_note="note de fin",
            custom_fields=[
                {
                    "title": "titre",
                    "fields": [
                        {
                            "id": "person",
                            "type": "person",
                            "label": "Personne",
                            "allow_self": False,
                            "required": True,
                        }
                    ],
                }
            ],
        )

        form_class = get_people_form_class(person_form)
        form = form_class(data={"person": "test@example.com"}, instance=self.person)
        self.assertFalse(form.is_valid())
        form.has_error("person", code="selected_self")

        person_form.custom_fields[0]["fields"][0]["allow_self"] = True

        form_class = get_people_form_class(person_form)
        form = form_class(data={"person": "test@example.com"}, instance=self.person)
        self.assertTrue(form.is_valid())

    # utilise un token bucket
    @using_separate_redis_server
    def test_person_choice_field(self):
        self.client.force_login(self.person.role)

        self.complex_form = PersonForm.objects.create(
            title="Formulaire person choice",
            slug="formulaire-person-choice",
            description="Ma description onsef",
            confirmation_note="Ma note de fin",
            custom_fields=[
                {
                    "title": "Détails",
                    "fields": [
                        {
                            "id": "person_choice",
                            "type": "person",
                            "label": "Un autre inscrit",
                        }
                    ],
                }
            ],
        )

        res = self.client.post(
            reverse("view_person_form", args=["formulaire-person-choice"]),
            data={"person_choice": "test2@example.com"},
        )
        self.assertRedirects(res, "/formulaires/formulaire-person-choice/confirmation/")
        submission = PersonFormSubmission.objects.last()
        self.assertEqual(submission.data["person_choice"], str(self.other_person.pk))

        for i in range(0, 20):
            self.client.post(
                reverse("view_person_form", args=["formulaire-person-choice"]),
                data={"person_choice": "notexistperson@corp.com"},
            )
        res = self.client.post(
            reverse("view_person_form", args=["formulaire-person-choice"]),
            data={"person_choice": "test2@example.com"},
        )
        self.assertFormError(
            res,
            "form",
            "person_choice",
            "Vous avez fait trop d'erreurs. Par sécurité, vous devez attendre avant d'essayer d'autres adresses emails.",
        )


class CampaignTemplateTestCase(SetUpPersonFormsMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.template_campaign = Campaign.objects.create(
            message_content_html="<title>[custom-field]</title>",
            message_mosaico_data="{}",
        )
        self.complex_form.campaign_template = self.template_campaign
        self.complex_form.save()

    def test_create_campaign_when_fill_form(self):
        res = self.client.post(
            "/formulaires/formulaire-complexe/",
            data={
                "tag": "tag2",
                "contact_phone": "06 34 56 78 90",
                "custom-field": "Super titre<script>alert('xss');{{ malicious_template }}",
                "custom-person-field": "valeur du champ libre avec person_field true",
            },
        )
        self.assertRedirects(res, "/formulaires/formulaire-complexe/confirmation/")
        self.assertEqual(Campaign.objects.all().count(), 2)
        self.assertEqual(
            Campaign.objects.last().message_content_html,
            "<title>Super titre&lt;script&gt;alert(&#x27;xss&#x27;); malicious_template }}</title>",
        )
