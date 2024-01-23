from rest_framework.test import APITestCase

from agir.groups.models import SupportGroup
from agir.people.models import Person


class PersonProfileTestCase(APITestCase):
    def setUp(self):
        self.person = Person.objects.create_person(
            "person@email.com", create_role=True, display_name="Person"
        )

    def test_can_retrieve_profile_options(self):
        res = self.client.options("/api/user/profile/")
        self.assertEqual(res.status_code, 200)

    def test_anonymous_user_cannot_retrieve_profile(self):
        self.client.logout()
        res = self.client.get("/api/user/profile/")
        self.assertEqual(res.status_code, 401)

    def test_authenticated_user_can_retrieve_her_profile(self):
        self.client.force_login(self.person.role)
        res = self.client.get("/api/user/profile/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["displayName"], self.person.display_name)

    def test_anonymous_user_cannot_update_profile(self):
        self.client.logout()
        new_data = {
            "displayName": "PP",
        }
        res = self.client.put("/api/user/profile/", data=new_data)
        self.assertEqual(res.status_code, 401)

    def test_authenticated_user_can_update_her_profile(self):
        self.client.force_login(self.person.role)
        new_data = {"displayName": "PP"}
        res = self.client.put("/api/user/profile/", data=new_data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["displayName"], "PP")
        self.person.refresh_from_db()
        self.assertEqual(self.person.display_name, "PP")


class SignupAPITestCase(APITestCase):
    def setUp(self):
        self.existing_person = Person.objects.create_person(
            "existing@pers.on", create_role=True
        )

    def test_cannot_subscribe_without_payload(self):
        self.client.logout()
        res = self.client.post("/api/inscription/")
        self.assertEqual(res.status_code, 422)
        self.assertIn("email", res.data)
        self.assertIn("location_zip", res.data)

    def test_cannot_subscribe_without_email(self):
        self.client.logout()
        data = {"email": None, "zip": "75019"}
        res = self.client.post("/api/inscription/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("email", res.data)

    def test_cannot_subscribe_with_invalid_email(self):
        self.client.logout()
        data = {"email": "not an email", "location_zip": "75019"}
        res = self.client.post("/api/inscription/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("email", res.data)

    def test_cannot_subscribe_without_zip(self):
        self.client.logout()
        data = {"email": "valid@ema.il", "location_zip": ""}
        res = self.client.post("/api/inscription/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("location_zip", res.data)

    # TODO: Restore zip code validation with international zip code handling
    # def test_cannot_subscribe_with_invalid_zip(self):
    #     self.client.logout()
    #     data = {"email": "valid@ema.il", "location_zip": "not a ZIP"}
    #     res = self.client.post("/api/inscription/", data=data)
    #     self.assertEqual(res.status_code, 422)
    #     self.assertIn("location_zip", res.data)

    def test_can_subscribe_with_valid_data(self):
        self.client.logout()
        data = {"email": "valid@ema.il", "location_zip": "75019"}
        res = self.client.post("/api/inscription/", data=data)
        self.assertEqual(res.status_code, 201)

    def test_no_error_is_returned_for_existing_email(self):
        self.client.logout()
        data = {"email": self.existing_person.email, "location_zip": "75019"}
        res = self.client.post("/api/inscription/", data=data)
        self.assertEqual(res.status_code, 201)


class CreateContactAPITestCase(APITestCase):
    def setUp(self):
        self.group = SupportGroup.objects.create(name="Groupe")
        self.subscriber = Person.objects.create_person(
            "subscriber@agir.local", create_role=True
        )
        self.existing_person = Person.objects.create_person(
            "une__personne@quiexiste.deja", create_role=True
        )
        self.valid_data = {
            "firstName": "Foo",
            "lastName": "Bar",
            "email": "contact@agir.local",
            "phone": "06 00 00 00 00",
            "address": "25 passage Dubail",
            "city": "Paris",
            "country": "FR",
            "zip": "75010",
            "subscribed": True,
            "isLiaison": False,
            "group": str(self.group.id),
            "hasGroupNotifications": False,
        }

    def test_anonymous_cannot_create_a_contact(self):
        self.client.logout()
        res = self.client.post("/api/contacts/creer/", data=self.valid_data)
        self.assertEqual(res.status_code, 401)

    def test_cannot_create_a_contact_without_first_name(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data}
        data.pop("firstName")
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("firstName", res.data)

    def test_cannot_create_a_contact_without_last_name(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data}
        data.pop("lastName")
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("lastName", res.data)

    def test_cannot_create_a_contact_without_email_and_phone(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data}
        data.pop("email")
        data.pop("phone")
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("global", res.data)

    def test_cannot_create_a_contact_with_invalid_email(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "email": "not an email"}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("email", res.data)

    def test_cannot_create_a_contact_without_zip_code(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data}
        data.pop("zip")
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("zip", res.data)

    def test_cannot_create_a_contact_with_invalid_phone(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "phone": "not a phone number"}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("phone", res.data)

    def test_cannot_create_a_contact_with_an_empty_address(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "address": ""}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("address", res.data)

    def test_cannot_create_a_contact_with_an_empty_city(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "city": ""}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("city", res.data)

    def test_cannot_create_a_contact_with_an_empty_country(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "country": ""}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("country", res.data)

    def test_cannot_create_a_contact_with_an_invalid_country(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "country": "not a country code"}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("country", res.data)

    def test_cannot_create_a_contact_with_an_invalid_group(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "group": "not a group id"}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 422)
        self.assertIn("group", res.data)

    def test_can_create_a_new_contact_with_valid_data(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 201)
        person_pk = res.data.get("id")
        self.assertTrue(
            Person.objects.get(pk=person_pk).subscribed == data["subscribed"]
        )

    def test_can_create_a_new_contact_withouth_email_if_phone_is_given(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data}
        data.pop("email")
        data["phone"] = "06 12 34 56 78"
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 201)
        person_pk = res.data.get("id")
        self.assertTrue(
            Person.objects.get(pk=person_pk).subscribed == data["subscribed"]
        )

    def test_can_update_a_contact_with_valid_data(self):
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "email": self.existing_person.primary_email.address}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 201)

    def test_a_membership_is_created_for_the_contact_with_a_group_id(self):
        email = "groupfollower@agir.local"
        self.client.force_login(user=self.subscriber.role)
        data = {**self.valid_data, "email": email}
        data.pop("group")
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertEqual(res.status_code, 201)
        person = Person.objects.get(pk=res.data.get("id"))
        self.assertFalse(self.group.members.filter(id=person.id).exists())
        data = {**self.valid_data, "email": email}
        res = self.client.post("/api/contacts/creer/", data=data)
        self.assertTrue(self.group.members.filter(id=person.id).exists())
