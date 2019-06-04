from django.test import TestCase
from django.urls import reverse

from agir.people.models import Person


class AddEmailTestCase(TestCase):
    def setUp(self) -> None:
        self.admin = Person.objects.create_superperson(
            "admin@agir.local", password="truc"
        )
        self.user1 = Person.objects.create_person("user1@agir.local")
        self.user2 = Person.objects.create_person("user2@agir.local")

        self.client.force_login(
            self.admin.role, backend="agir.people.backend.PersonBackend"
        )

        self.change_url = reverse("admin:people_person_change", args=[self.user1.pk])
        self.add_email_url = reverse(
            "admin:people_person_addemail", args=[self.user1.pk]
        )
        self.merge_url = f'{reverse("admin:people_person_merge")}?id={self.user1.pk}&id={self.user2.pk}'

    def test_can_display_pages(self):
        res = self.client.get(self.add_email_url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'name="email"')

        res = self.client.get(self.merge_url)
        self.assertEqual(res.status_code, 200)

        self.assertContains(res, f'value="{self.user1.pk}"')
        self.assertContains(res, f'value="{self.user2.pk}"')

    def test_can_add_email(self):
        res = self.client.post(self.add_email_url, data={"email": "user1@example.com"})
        self.assertRedirects(res, self.change_url)

        self.assertEqual(self.user1.email, "user1@example.com")

    def test_can_merge_people(self):
        res = self.client.post(self.add_email_url, data={"email": "user2@agir.local"})
        self.assertRedirects(res, self.merge_url)

        res = self.client.post(
            self.merge_url, data={"primary_account": str(self.user1.pk)}
        )
        self.assertRedirects(res, self.change_url)

        self.assertFalse(Person.objects.filter(pk=self.user2.pk).exists())

        self.assertCountEqual(
            [e.address for e in self.user1.emails.all()],
            ["user1@agir.local", "user2@agir.local"],
        )
