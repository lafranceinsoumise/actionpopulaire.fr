from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase

from agir.events.models import Event, RSVP
from agir.groups.models import SupportGroup, Membership
from agir.people.models import Person, PersonTag
from agir.people.viewsets import LegacyPersonViewSet


class LegacyPersonEndpointTestCase(APITestCase):
    def as_viewer(self, request):
        force_authenticate(request, self.viewer_person.role)

    def setUp(self):
        self.basic_person = Person.objects.create_insoumise(
            email="jean.georges@domain.com",
            first_name="Jean",
            last_name="Georges",
            create_role=True,
        )

        self.viewer_person = Person.objects.create_insoumise(
            email="viewer@viewer.fr", create_role=True
        )

        self.adder_person = Person.objects.create_insoumise(
            email="adder@adder.fr", create_role=True
        )

        self.changer_person = Person.objects.create_insoumise(
            email="changer@changer.fr", create_role=True
        )

        person_content_type = ContentType.objects.get_for_model(Person)
        view_permission = Permission.objects.get(
            content_type=person_content_type, codename="view_person"
        )
        add_permission = Permission.objects.get(
            content_type=person_content_type, codename="add_person"
        )
        change_permission = Permission.objects.get(
            content_type=person_content_type, codename="change_person"
        )

        self.viewer_person.role.user_permissions.add(view_permission)
        self.adder_person.role.user_permissions.add(add_permission)
        self.changer_person.role.user_permissions.add(
            view_permission, change_permission
        )

        self.event = Event.objects.create(
            name="event",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=2),
        )

        self.rsvp = RSVP.objects.create(person=self.basic_person, event=self.event)

        self.supportgroup = SupportGroup.objects.create(name="Group")

        self.membership = Membership.objects.create(
            person=self.basic_person, supportgroup=self.supportgroup
        )

        self.factory = APIRequestFactory()

        self.detail_view = LegacyPersonViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )

        self.list_view = LegacyPersonViewSet.as_view({"get": "list", "post": "create"})

    def test_cannot_list_while_unauthenticated(self):
        request = self.factory.get("")
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_only_view_self_while_unprivileged(self):
        request = self.factory.get("")
        force_authenticate(request, self.basic_person.role)
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["_items"]), 1)
        self.assertEqual(response.data["_items"][0]["_id"], str(self.basic_person.pk))

    def test_can_see_self_while_authenticated(self):
        self.client.force_authenticate(self.basic_person.role)
        response = self.client.get("/legacy/people/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["_id"], str(self.basic_person.pk))

    def test_cannot_see_self_while_unauthenticated(self):
        response = self.client.get("/legacy/people/me/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_view_details_while_unauthenticated(self):
        request = self.factory.get("")
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_see_self_while_unprivileged(self):
        request = self.factory.get("")
        force_authenticate(request, self.basic_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_view_others_details_while_unprivileged(self):
        request = self.factory.get("")
        force_authenticate(request, self.basic_person.role)
        response = self.detail_view(request, pk=self.viewer_person.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_contain_simple_fields(self):
        request = self.factory.get("")
        self.as_viewer(request)
        response = self.detail_view(request, pk=self.basic_person.pk)

        expected_fields = {
            "_id",
            "id",
            "email",
            "first_name",
            "last_name",
            "bounced",
            "bounced_date",
        }

        assert expected_fields.issubset(set(response.data))

    def test_contains_only_whitelisted_fields_while_unprivileged(self):
        self.client.force_authenticate(self.basic_person.role)
        response = self.client.get("/legacy/people/me/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(
            (
                "url",
                "_id",
                "email",
                "first_name",
                "last_name",
                "email_opt_in",
                "location",
            ),
            response.data.keys(),
        )

    def test_return_correct_values(self):
        request = self.factory.get("")
        self.as_viewer(request)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.basic_person.email, response.data["email"])
        self.assertEqual(self.basic_person.first_name, response.data["first_name"])
        self.assertEqual(self.basic_person.last_name, response.data["last_name"])

    def test_cannot_post_new_person_while_unauthenticated(self):
        request = self.factory.post(
            "",
            data={
                "email": "jean-luc@melenchon.fr",
                "first_name": "Jean-Luc",
                "last_name": "Mélenchon",
            },
        )
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_post_new_person(self):
        request = self.factory.post(
            "",
            data={
                "email": "jean-luc@melenchon.fr",
                "first_name": "Jean-Luc",
                "last_name": "Mélenchon",
            },
        )
        force_authenticate(request, self.adder_person.role)
        response = self.list_view(request)

        # assert it worked
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        new_person = Person.objects.get(email="jean-luc@melenchon.fr")

        self.assertEqual(new_person.first_name, "Jean-Luc")
        self.assertEqual(new_person.last_name, "Mélenchon")

    def test_cannot_post_new_person_with_existing_email(self):
        request = self.factory.post("", data={"email": self.basic_person.email})
        force_authenticate(request, self.adder_person.role)
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_can_update_email_list(self):
        """
        We test at the same time that we can replace the list,
        and that we can set the primary email with the 'email' field
        """
        request = self.factory.patch(
            "",
            data={
                "emails": [
                    {"address": "test@example.com", "bounced": True},
                    {"address": "testprimary@example.com", "bounced": False},
                    {"address": "jean.georges@domain.com"},
                ],
                "email": "testprimary@example.com",
            },
        )
        force_authenticate(request, self.changer_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.basic_person.email, "testprimary@example.com")
        self.assertEqual(self.basic_person.emails.all()[2].address, "test@example.com")
        self.assertEqual(self.basic_person.emails.all()[2].bounced, True)

    def test_can_update_bounced_status(self):
        request = self.factory.patch("", data={"bounced": True})
        force_authenticate(request, self.changer_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.basic_person.emails.all()[0].address, "jean.georges@domain.com"
        )
        self.assertEqual(self.basic_person.emails.all()[0].bounced, True)
        self.assertLess(self.basic_person.emails.all()[0].bounced_date, timezone.now())

    def test_cannot_modify_while_unauthenticated(self):
        request = self.factory.patch("", data={"first_name": "Marc"})
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_modify_self(self):
        request = self.factory.patch(
            "", data={"email": "marcus@cool.md", "first_name": "Marc"}
        )
        force_authenticate(request, self.basic_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.basic_person.refresh_from_db()
        self.assertEqual(self.basic_person.first_name, "Marc")
        self.assertTrue(
            self.basic_person.emails.filter(address="marcus@cool.md").exists()
        )

    def test_can_modify_with_global_perm(self):
        request = self.factory.patch("", data={"first_name": "Marc"})
        force_authenticate(request, self.changer_person.role)
        response = self.detail_view(request, pk=self.basic_person.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.basic_person.refresh_from_db()
        self.assertEqual(self.basic_person.first_name, "Marc")

    def test_can_list_persons(self):
        request = self.factory.get("")
        self.as_viewer(request)
        response = self.list_view(request)

        self.assertIn("_items", response.data)
        self.assertIn("_meta", response.data)

        self.assertEqual(len(response.data["_items"]), 4)
        self.assertCountEqual(
            [person["email"] for person in response.data["_items"]],
            [
                "jean.georges@domain.com",
                "adder@adder.fr",
                "changer@changer.fr",
                "viewer@viewer.fr",
            ],
        )

    def test_can_post_users_with_empty_null_and_blank_fields(self):
        request = self.factory.post(
            "",
            data={
                "email": "putain@demerde.com",
                "location_address1": "",
                "location_address2": None,
                "country_code": None,
            },
        )
        force_authenticate(request, self.adder_person.role)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LegacyEndpointFieldsTestCase(TestCase):
    def get_request(self, path="", data=None, **extra):
        return self.as_superuser(self.factory.get(path, data, **extra))

    def patch_request(self, path="", data=None, **extra):
        return self.as_superuser(self.factory.patch(path, data, **extra))

    def as_superuser(self, request):
        force_authenticate(request, self.superuser.role)
        return request

    def setUp(self):
        self.superuser = Person.objects.create_superperson(
            "super@user.fr", None, create_role=True
        )

        self.tag = PersonTag.objects.create(label="tag1")

        self.person1 = Person.objects.create_insoumise("person1@domain.fr")
        self.person2 = Person.objects.create_insoumise(
            email="person2@domain.fr", nb_id=12345
        )
        self.person3 = Person.objects.create_insoumise(
            email="person3@domain.fr", nb_id=67890
        )

        self.detail_view = LegacyPersonViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )

        self.list_view = LegacyPersonViewSet.as_view({"get": "list", "post": "create"})

        self.factory = APIRequestFactory()

    def test_can_add_existing_tag(self):
        request = self.patch_request(data={"tags": ["tag1"]})

        response = self.detail_view(request, pk=self.person1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.person1.refresh_from_db()

        self.assertCountEqual(self.person1.tags.all(), [self.tag])

    def test_can_add_new_tag(self):
        request = self.patch_request(data={"tags": ["tag2"]})

        response = self.detail_view(request, pk=self.person1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        qs = PersonTag.objects.filter(label="tag2")
        self.person1.refresh_from_db()
        self.assertEqual(len(qs), 1)
        self.assertCountEqual(qs, self.person1.tags.all())

    def test_can_update_location_fields(self):
        request = self.patch_request(
            data={
                "location": {
                    "address": "40 boulevard Auguste Blanqui, 75013 Paris, France",
                    "address1": "40 boulevard Auguste Blanqui",
                    "city": "Paris",
                    "country_code": "FR",
                    "zip": "75013",
                }
            }
        )

        response = self.detail_view(request, pk=self.person1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.person1.refresh_from_db()

        self.assertEqual(
            self.person1.location_address,
            "40 boulevard Auguste Blanqui, 75013 Paris, France",
        )
        self.assertEqual(self.person1.location_address1, "40 boulevard Auguste Blanqui")
        self.assertEqual(self.person1.location_city, "Paris")
        self.assertEqual(self.person1.location_country.code, "FR")
        self.assertEqual(self.person1.location_zip, "75013")


class LegacyEndpointLookupFilterTestCase(TestCase):
    def get_request(self, path="", data=None, **extra):
        return self.as_superuser(self.factory.get(path, data, **extra))

    def as_superuser(self, request):
        force_authenticate(request, self.superuser.role)
        return request

    def setUp(self):
        self.superuser = Person.objects.create_superperson("super@user.fr", None)
        self.person1 = Person.objects.create_insoumise("person1@domain.fr")
        self.person2 = Person.objects.create_insoumise(
            email="person2@domain.fr", nb_id=12345
        )
        self.person3 = Person.objects.create_insoumise(
            email="person3@domain.fr", nb_id=67890
        )

        self.detail_view = LegacyPersonViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        )

        self.list_view = LegacyPersonViewSet.as_view({"get": "list", "post": "create"})

        self.factory = APIRequestFactory()

    def test_can_query_by_pk(self):
        request = self.get_request()

        response = self.detail_view(request, pk=self.person1.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.person1.email)

    def test_can_query_by_nb_id(self):
        request = self.get_request()

        response = self.detail_view(request, pk=self.person2.nb_id)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.person2.email)

    def test_can_filter_by_email(self):
        request = self.get_request(data={"email": "person1@domain.fr"})
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["_items"]), 1)
