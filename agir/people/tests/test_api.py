from rest_framework.test import APITestCase

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
