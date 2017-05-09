from django.test import TestCase
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point

from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework import status

from .models import SupportGroup, Membership
from people.models import Person
from .viewsets import LegacySupportGroupViewSet


class BasicSupportGroupTestCase(TestCase):
    def test_can_create_support_group(self):
        group = SupportGroup.objects.create(
            name="Groupe d'appui",
        )


class MembershipTestCase(TestCase):
    def setUp(self):
        self.support_group = SupportGroup.objects.create(
            name='Test',
        )

        self.person = Person.objects.create(
            email='marc.machin@truc.com'
        )

    def test_can_create_membership(self):
        Membership.objects.create(
            support_group=self.support_group,
            person=self.person,
        )

    def test_cannot_create_without_person(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                support_group=self.support_group,
            )

    def test_cannot_create_without_support_group(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person,
            )

    def test_unique_membership(self):
        Membership.objects.create(
            person=self.person,
            support_group=self.support_group
        )

        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person,
                support_group=self.support_group
            )


class LegacySupportGroupViewSetTestCase(TestCase):
    def setUp(self):
        self.support_group = SupportGroup.objects.create(
            name='event',
        )

        self.unprivileged_person = Person.objects.create_person(
            email='jean.georges@domain.com',
            first_name='Jean',
            last_name='Georges',
        )

        self.adder_person = Person.objects.create_person(
            email='adder@adder.fr',
        )

        self.changer_person = Person.objects.create_person(
            email='changer@changer.fr'
        )

        self.one_event_person = Person.objects.create_person(
            email='event@event.com'
        )

        event_content_type = ContentType.objects.get_for_model(SupportGroup)
        add_permission = Permission.objects.get(content_type=event_content_type, codename='add_supportgroup')
        change_permission = Permission.objects.get(content_type=event_content_type, codename='change_supportgroup')

        self.adder_person.role.user_permissions.add(add_permission)
        self.changer_person.role.user_permissions.add(change_permission)

        Membership.objects.create(
            support_group=self.support_group,
            person=self.one_event_person,
            is_referent=True,
        )

        self.detail_view = LegacySupportGroupViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })

        self.list_view = LegacySupportGroupViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.new_group_data = {
            'name': 'event 2',
        }

        self.factory = APIRequestFactory()

    def can_list_groups_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)

        item = response.data['_items'][0]

        self.assertEqual(item['_id'], str(self.support_group.pk))

    def test_can_see_group_details_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.support_group.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.support_group.pk))

    def test_cannot_create_group_while_unauthenticated(self):
        request = self.factory.post('', data=self.new_group_data)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_group_while_unauthenticated(self):
        request = self.factory.put('', data=self.new_group_data)

        response = self.detail_view(request, pk=self.support_group.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_group_without_permission(self):
        request = self.factory.put('', data=self.new_group_data)
        force_authenticate(request, self.unprivileged_person.role)

        response = self.detail_view(request, pk=self.support_group.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_create_group_with_global_perm(self):
        request = self.factory.post('', data=self.new_group_data)
        force_authenticate(request, self.adder_person.role)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        support_groups = SupportGroup.objects.all()

        self.assertEqual(len(support_groups), 2)

    def test_can_modify_group_with_global_perm(self):
        request = self.factory.patch('', data={
            'description': 'Plus mieux!'
        })

        force_authenticate(request, user=self.changer_person.role)

        response = self.detail_view(request, pk=self.support_group.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.support_group.refresh_from_db()

        self.assertEqual(self.support_group.description, 'Plus mieux!')

    def test_referent_can_modify_group(self):
        request = self.factory.patch('', data={
            'description': 'Plus mieux!'
        })

        force_authenticate(request, user=self.one_event_person.role)

        response = self.detail_view(request, pk=self.support_group.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.support_group.refresh_from_db()

        self.assertEqual(self.support_group.description, 'Plus mieux!')


class FiltersTestCase(TestCase):
    def get_request(self, path='', data=None, **extra):
        return self.as_superuser(self.factory.get(path, data, **extra))

    def as_superuser(self, request):
        force_authenticate(request, self.superuser.role)
        return request

    def setUp(self):
        self.superuser = Person.objects.create_superperson('super@user.fr', None)

        tz = timezone.get_default_timezone()

        self.paris_group = SupportGroup.objects.create(
            name='Paris',
            nb_id=1,
            coordinates=Point(2.349722, 48.853056),  # ND de Paris
        )

        self.amiens_group = SupportGroup.objects.create(
            name='Amiens',
            nb_path='/amiens',
            coordinates=Point(2.301944, 49.8944),  # ND d'Amiens
        )

        self.marseille_group = SupportGroup.objects.create(
            name='Marseille',
            coordinates=Point(5.36472, 43.30028),  # Saint-Marie-Majeure de Marseille
        )

        self.eiffel_coordinates = [2.294444, 48.858333]

        self.factory = APIRequestFactory()

        self.list_view = LegacySupportGroupViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.detail_view = LegacySupportGroupViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy',
        })

    def test_can_query_by_pk(self):
        request = self.get_request()

        response = self.detail_view(request, pk=self.paris_group.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.paris_group.name)

    def test_can_query_by_nb_id(self):
        request = self.get_request()

        response = self.detail_view(request, pk=str(self.paris_group.nb_id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.paris_group.pk))

    def test_filter_coordinates_no_results(self):
        # la tour eiffel est à plus d'un kilomètre de Notre-Dame
        filter_string = '{"maxDistance": 1000, "coordinates": %r}' % (self.eiffel_coordinates,)

        request = self.factory.get('', data={
            'closeTo': filter_string
        })

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 0)

    def test_filter_coordinates_one_result(self):
        # la tour eiffel est à moins de 10 km de Notre-Dame
        filter_string = '{"maxDistance": 10000, "coordinates": %r}' % (self.eiffel_coordinates,)

        request = self.factory.get('', data={
            'closeTo': filter_string,
        })

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)
        self.assertEqual(response.data['_items'][0]['_id'], str(self.paris_group.pk))

    def test_filter_by_path(self):
        request = self.factory.get('', data={
            'path': '/amiens',
        })

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)
        self.assertEqual(response.data['_items'][0]['_id'], str(self.amiens_group.pk))
