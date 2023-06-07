from django.test import TestCase
from rest_framework.reverse import reverse

from agir.people.models import Person


class NavsProfileMixinTestCase(TestCase):
    def setUp(self):
        super().setUp()

        self.person = Person.objects.create_insoumise("test@test.com", create_role=True)
        self.client.force_login(self.person.role)

    def test_can_see_insoumis_menu(self):
        response = self.client.get(reverse("contact"))

        self.assertContains(response, reverse("personal_information"))
        self.assertContains(response, reverse("contact"))
        self.assertContains(response, reverse("skills"))
        self.assertContains(response, reverse("volunteer"))
        self.assertContains(response, reverse(("personal_data")))
