from unittest import skip

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from agir.api.redis import using_separate_redis_server
from agir.municipales.models import CommunePage
from agir.people.models import Person

BLAGNY_WKT = (
    "SRID=4326;MULTIPOLYGON (((5.211068 49.639615, 5.213468 49.639336, 5.219574 49.64074, 5.219381 49.64023, "
    "5.223847 49.64063, 5.223955 49.640164, 5.222261 49.64004, 5.222636 49.638293, 5.220239 49.638258, "
    "5.217761 49.637414, 5.218495 49.636798, 5.215894 49.634411, 5.218192 49.634127, 5.220692 49.632016, "
    "5.222412 49.63247, 5.223132 49.631554, 5.219957 49.629837, 5.218153 49.62831, 5.216203 49.627863, "
    "5.213808 49.62603, 5.212037 49.625582, 5.214041 49.624643, 5.213677 49.622282, 5.212457 49.621295, "
    "5.211704 49.618632, 5.210719 49.618761, 5.21059 49.615752, 5.211287 49.614745, 5.208299 49.612769, "
    "5.205184 49.61215, 5.204202 49.611353, 5.205283 49.6104, 5.205098 49.608871, 5.204503 49.609092, "
    "5.198994 49.606375, 5.196094 49.608197, 5.19316 49.608391, 5.19125 49.605722, 5.184964 49.607717, "
    "5.184315 49.608154, 5.1852 49.609714, 5.184634 49.610557, 5.182803 49.611487, 5.184503 49.613538, "
    "5.183421 49.614609, 5.181445 49.615646, 5.182148 49.616117, 5.179222 49.617667, 5.175176 49.619395, "
    "5.176085 49.620014, 5.175095 49.622009, 5.173669 49.622963, 5.174129 49.624128, 5.176745 49.627202, "
    "5.177724 49.62675, 5.179023 49.627524, 5.181019 49.627726, 5.184359 49.63154, 5.186552 49.631165, "
    "5.186953 49.632379, 5.18918 49.632679, 5.190296 49.633329, 5.191875 49.632495, 5.194262 49.632413, "
    "5.196508 49.634301, 5.209807 49.639063, 5.211068 49.639615))) "
)


@using_separate_redis_server
@skip("Skipping during elections to avoid conflicts")
class ProcurationTestCase(TestCase):
    def setUp(self):
        self.commune = CommunePage.objects.create(
            code="08067",
            code_departement="08",
            slug="blagny",
            name="Blagny",
            published=True,
            tete_liste_tour_1="Marc Lefevre",
            coordinates=BLAGNY_WKT,
        )
        self.url = reverse(
            "procuration_commune",
            args=(self.commune.code_departement, self.commune.slug),
        )

    def test_cannot_access_when_not_published(self):
        self.commune.published = False
        self.commune.save()

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 404)

    def test_can_fill_in_form_when_not_logged_in(self):
        self.commune.contact_email = "test@contact.com"
        self.commune.save()

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            self.url,
            data={
                "nom": "Groing",
                "prenom": "Jean",
                "code_postal": "75003",
                "bureau": "0389",
                "email": "jean.groing@gmail.com",
                "phone": "0683920482",
                "autres": "Rien de spécial",
            },
        )
        self.assertRedirects(
            res,
            reverse(
                "view_commune", args=(self.commune.code_departement, self.commune.slug)
            ),
        )

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        self.assertEqual(message.to, ["test@contact.com"])
        self.assertIn("Jean Groing", message.body)
        self.assertIn("jean.groing@gmail.com", message.body)
        self.assertIn("0389", message.body)
        self.assertIn("+33 6 83 92 04 82", message.body)
        self.assertIn("Rien de spécial", message.body)

    # def test_can_subscribe(self):
    #     res = self.client.get(self.url)
    #     self.assertEqual(res.status_code, 200)
    #
    #     res = self.client.post(
    #         self.url,
    #         data={
    #             "nom": "Groing",
    #             "prenom": "Jean",
    #             "code_postal": "75003",
    #             "bureau": "0389",
    #             "email": "jean.groing@gmail.com",
    #             "phone": "0683920482",
    #             "autres": "Rien de spécial",
    #             "subscribed": True,
    #         },
    #     )
    #     self.assertRedirects(
    #         res,
    #         reverse(
    #             "view_commune", args=(self.commune.code_departement, self.commune.slug)
    #         ),
    #     )
    #
    #     self.assertEqual(len(mail.outbox), 2)
    #
    #     message = mail.outbox[1]
    #
    #     confirmation_url = reverse("subscription_confirm")
    #     match = re.search(confirmation_url + r'\?[^" \n)]+', message.body)
    #
    #     self.assertIsNotNone(match)
    #     url_with_params = match.group(0)
    #
    #     response = self.client.get(url_with_params)
    #     self.assertEqual(response.status_code, 200)
    #
    #     self.assertContains(response, "Bienvenue !")
    #
    #     p = Person.objects.get_by_natural_key("jean.groing@gmail.com")
    #     self.assertEqual(p.first_name, "Jean")
    #     self.assertEqual(p.last_name, "Groing")
    #     self.assertEqual(p.location_zip, "75003")
    #     self.assertEqual(p.contact_phone.as_international, "+33 6 83 92 04 82")
    #     self.assertTrue(p.subscribed)

    def test_can_update_existing_person(self):
        p = Person.objects.create_insoumise(
            "jean.groing@gmail.com", location_zip="75004"
        )

        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(
            self.url,
            data={
                "nom": "Groing",
                "prenom": "Jean",
                "code_postal": "75003",
                "bureau": "0389",
                "email": "jean.groing@gmail.com",
                "phone": "0683920482",
                "autres": "Rien de spécial",
                "subscribed": "Y",
            },
        )
        self.assertRedirects(
            res,
            reverse(
                "view_commune", args=(self.commune.code_departement, self.commune.slug)
            ),
        )

        p.refresh_from_db()

        self.assertEqual(p.first_name, "Jean")
        self.assertEqual(p.last_name, "Groing")
        self.assertEqual(p.location_zip, "75004")
        self.assertEqual(p.contact_phone.as_international, "+33 6 83 92 04 82")
