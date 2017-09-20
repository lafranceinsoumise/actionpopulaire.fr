from unittest import skip
from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point

from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from rest_framework import status
from rest_framework.reverse import reverse

from .models import SupportGroup, Membership
from people.models import Person
from .viewsets import LegacySupportGroupViewSet, MembershipViewSet, NestedMembershipViewSet


class BasicSupportGroupTestCase(TestCase):
    def test_can_create_supportgroup(self):
        group = SupportGroup.objects.create(
            name="Groupe d'appui",
        )


class MembershipTestCase(APITestCase):
    def setUp(self):
        self.supportgroup = SupportGroup.objects.create(
            name='Test',
        )

        self.person = Person.objects.create(
            email='marc.machin@truc.com'
        )

        self.privileged_user = Person.objects.create_superperson('super@user.fr', None)

    def test_can_create_membership(self):
        Membership.objects.create(
            supportgroup=self.supportgroup,
            person=self.person,
        )

    def test_can_get_membership(self):
        membership = Membership.objects.create(
            supportgroup=self.supportgroup,
            person=self.person,
        )

        self.client.force_authenticate(self.privileged_user.role)
        path = '/legacy/memberships/' + str(membership.id) + '/'
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertIn(path, str(response.data['url']))

    def test_cannot_create_without_person(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                supportgroup=self.supportgroup,
            )

    def test_cannot_create_without_supportgroup(self):
        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person,
            )

    def test_unique_membership(self):
        Membership.objects.create(
            person=self.person,
            supportgroup=self.supportgroup
        )

        with self.assertRaises(IntegrityError):
            Membership.objects.create(
                person=self.person,
                supportgroup=self.supportgroup
            )


class LegacySupportGroupViewSetTestCase(TestCase):
    def setUp(self):
        self.supportgroup = SupportGroup.objects.create(
            name='Groupe',
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

        self.view_all_person = Person.objects.create_person(
            email='viewer@viewer.fr'
        )

        self.one_person_group = Person.objects.create_person(
            email='group@group.com'
        )

        group_content_type = ContentType.objects.get_for_model(SupportGroup)
        add_permission = Permission.objects.get(content_type=group_content_type, codename='add_supportgroup')
        change_permission = Permission.objects.get(content_type=group_content_type, codename='change_supportgroup')
        view_hidden_permission = Permission.objects.get(content_type=group_content_type, codename='view_hidden_supportgroup')

        self.adder_person.role.user_permissions.add(add_permission)
        self.changer_person.role.user_permissions.add(change_permission)
        self.view_all_person.role.user_permissions.add(view_hidden_permission)

        Membership.objects.create(
            supportgroup=self.supportgroup,
            person=self.one_person_group,
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
            'name': 'group 2',
        }

        self.factory = APIRequestFactory()

    def test_can_list_groups_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 1)

        item = response.data['_items'][0]

        self.assertEqual(item['_id'], str(self.supportgroup.pk))

    def unpublish_group(self):
        self.supportgroup.published = False
        self.supportgroup.save()

    def test_cannot_list_unpublished_groups_while_unauthicated(self):
        self.unpublish_group()
        request = self.factory.get('')
        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 0)

    def test_can_see_group_details_while_unauthenticated(self):
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.supportgroup.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.supportgroup.pk))

    def test_cannot_view_unpublished_groups_while_unauthicated(self):
        self.unpublish_group()
        request = self.factory.get('')
        response = self.detail_view(request, pk=self.supportgroup.pk)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_view_unpublished_groups_with_correct_permissions(self):
        self.unpublish_group()
        request = self.factory.get('')
        force_authenticate(request, self.view_all_person.role)
        response = self.detail_view(request, pk=self.supportgroup.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['_id'], str(self.supportgroup.pk))

    def test_cannot_create_group_while_unauthenticated(self):
        request = self.factory.post('', data=self.new_group_data)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_group_while_unauthenticated(self):
        request = self.factory.put('', data=self.new_group_data)

        response = self.detail_view(request, pk=self.supportgroup.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_modify_group_without_permission(self):
        request = self.factory.put('', data=self.new_group_data)
        force_authenticate(request, self.unprivileged_person.role)

        response = self.detail_view(request, pk=self.supportgroup.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_create_group_with_global_perm(self):
        request = self.factory.post('', data=self.new_group_data)
        force_authenticate(request, self.adder_person.role)

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        supportgroups = SupportGroup.objects.all()

        self.assertEqual(len(supportgroups), 2)

    def test_can_modify_group_with_global_perm(self):
        request = self.factory.patch('', data={
            'description': 'Plus mieux!'
        })

        force_authenticate(request, user=self.changer_person.role)

        response = self.detail_view(request, pk=self.supportgroup.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.supportgroup.refresh_from_db()

        self.assertEqual(self.supportgroup.description, 'Plus mieux!')

    def test_referent_can_modify_group(self):
        request = self.factory.patch('', data={
            'description': 'Plus mieux!'
        })

        force_authenticate(request, user=self.one_person_group.role)

        response = self.detail_view(request, pk=self.supportgroup.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.supportgroup.refresh_from_db()

        self.assertEqual(self.supportgroup.description, 'Plus mieux!')


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
        filter_string = '{"max_distance": 1000, "coordinates": %r}' % (self.eiffel_coordinates,)

        request = self.factory.get('', data={
            'close_to': filter_string
        })

        response = self.list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('_items', response.data)
        self.assertEqual(len(response.data['_items']), 0)

    def test_filter_coordinates_one_result(self):
        # la tour eiffel est à moins de 10 km de Notre-Dame
        filter_string = '{"max_distance": 10000, "coordinates": %r}' % (self.eiffel_coordinates,)

        request = self.factory.get('', data={
            'close_to': filter_string,
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


class MembershipEndpointTestCase(TestCase):
    def get_request(self, path='', data=None, **extra):
        return self.factory.get(path, data, **extra)

    def as_privileged(self, request):
        force_authenticate(request, self.privileged_user.role)
        return request

    def as_organizer(self, request):
        force_authenticate(request, self.manager.role)
        return request

    def as_unprivileged(self, request):
        force_authenticate(request, self.unprivileged_person.role)
        return request

    def setUp(self):
        self.privileged_user = Person.objects.create_superperson('super@user.fr', None)

        self.organizer = Person.objects.create_person(
            email='supportgroup@supportgroup.com'
        )

        self.unprivileged_person = Person.objects.create_person(
            email='unprivileged@supportgroup.com',
        )

        tz = timezone.get_default_timezone()

        self.supportgroup = SupportGroup.objects.create(
            name='Paris+June',
            nb_id=1,
            coordinates=Point(2.349722, 48.853056),  # ND de Paris
        )

        self.secondary_supportgroup = SupportGroup.objects.create(
            name='Amiens+July',
            nb_path='/amiens_july',
            coordinates=Point(2.301944, 49.8944),  # ND d'Amiens
        )

        self.unprivileged_membership = Membership.objects.create(
            supportgroup=self.supportgroup,
            person=self.unprivileged_person,
        )

        self.organizer_membership = Membership.objects.create(
            supportgroup=self.supportgroup,
            person=self.organizer,
            is_referent=True,
            is_manager=True
        )

        self.other_membership = Membership.objects.create(
            supportgroup=self.secondary_supportgroup,
            person=self.unprivileged_person
        )

        membership_content_type = ContentType.objects.get_for_model(Membership)
        add_permission = Permission.objects.get(content_type=membership_content_type, codename='add_membership')
        change_permission = Permission.objects.get(content_type=membership_content_type, codename='change_membership')
        delete_permission = Permission.objects.get(content_type=membership_content_type, codename='delete_membership')

        self.privileged_user.role.user_permissions.add(add_permission, change_permission, delete_permission)

        self.factory = APIRequestFactory()

        self.membership_list_view = MembershipViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.membership_detail_view = MembershipViewSet.as_view({
            'get'
        })

    def test_unauthenticated_cannot_see_any_memberships(self):
        request = self.get_request()

        response = self.membership_list_view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_see_own_memberships(self):
        request = self.as_unprivileged(self.get_request())

        response = self.membership_list_view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        assert all(
            membership['person'].split('/')[-2] == str(self.unprivileged_person.id) for membership in response.data)
        self.assertCountEqual([membership['supportgroup'].split('/')[-2] for membership in response.data],
                              [str(self.supportgroup.id), str(self.secondary_supportgroup.id)])

    @skip('TODO')
    def test_can_modify_own_membership(self):
        pass


class GroupMembershipEndpointTestCase(TestCase):
    def get_request(self, path='', data=None, **extra):
        return self.factory.get(path, data, **extra)

    def as_privileged(self, request):
        force_authenticate(request, self.privileged_user.role)
        return request

    def as_organizer(self, request):
        force_authenticate(request, self.manager.role)
        return request

    def as_unprivileged(self, request):
        force_authenticate(request, self.unprivileged_person.role)
        return request

    def setUp(self):
        self.privileged_user = Person.objects.create_superperson('super@user.fr', None)

        self.manager = Person.objects.create_person(
            email='event@event.com'
        )

        self.unprivileged_person = Person.objects.create_person(
            email='unprivileged@event.com',
        )

        tz = timezone.get_default_timezone()

        self.supportgroup = SupportGroup.objects.create(
            name='Paris',
            nb_id=1,
            coordinates=Point(2.349722, 48.853056),  # ND de Paris
        )

        self.secondary_supportgroup = SupportGroup.objects.create(
            name='Amiens',
            nb_path='/amiens',
            coordinates=Point(2.301944, 49.8944),  # ND d'Amiens
        )

        self.unprivileged_membership = Membership.objects.create(
            supportgroup=self.supportgroup,
            person=self.unprivileged_person,
        )

        self.manager_membership = Membership.objects.create(
            supportgroup=self.supportgroup,
            person=self.manager,
            is_referent=True,
            is_manager=True
        )

        self.other_event_membership = Membership.objects.create(
            supportgroup=self.secondary_supportgroup,
            person=self.unprivileged_person
        )

        membership_content_type = ContentType.objects.get_for_model(Membership)
        add_permission = Permission.objects.get(content_type=membership_content_type, codename='add_membership')
        change_permission = Permission.objects.get(content_type=membership_content_type, codename='change_membership')
        delete_permission = Permission.objects.get(content_type=membership_content_type, codename='delete_membership')

        self.privileged_user.role.user_permissions.add(add_permission, change_permission, delete_permission)

        self.factory = APIRequestFactory()

        self.membership_list_view = NestedMembershipViewSet.as_view({
            'get': 'list',
            'post': 'create'
        })

        self.membership_detail_view = NestedMembershipViewSet.as_view({
            'get'
        })

        self.membership_bulk_view = NestedMembershipViewSet.as_view({
            'put': 'bulk'
        })

    def test_unauthenticated_cannot_see_any_memberships(self):
        request = self.get_request()

        response = self.membership_list_view(request, parent_lookup_supportgroup=str(self.supportgroup.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_can_see_own_memberships(self):
        request = self.as_unprivileged(self.get_request())

        response = self.membership_list_view(request, parent_lookup_supportgroup=str(self.supportgroup.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['person'].split('/')[-2], str(self.unprivileged_person.id))

    def test_can_see_memberships_as_organizer(self):
        request = self.as_organizer(self.get_request())

        response = self.membership_list_view(request, parent_lookup_supportgroup=str(self.supportgroup.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertCountEqual(
            [membership['person'].split('/')[-2] for membership in response.data],
            [str(self.unprivileged_person.id), str(self.manager.id)]
        )

    def test_creation(self):
        request = self.factory.post('', data={
            'person': reverse('legacy:person-detail', kwargs={'pk': self.privileged_user.id}),
            'is_manager': True,
            'is_referent': True,
        })
        self.as_privileged(request)

        response = self.membership_list_view(request, parent_lookup_supportgroup=str(self.supportgroup.pk))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        qs = self.supportgroup.memberships.all()

        self.assertEqual(len(qs), 3)
        self.assertEqual(qs[2].person_id, self.privileged_user.id)
        self.assertEqual(qs[2].is_manager, True)
        self.assertEqual(qs[2].is_referent, True)

    def test_bulk_creation(self):
        request = self.factory.put('', data=[
            # modification
            {
                'person': reverse('legacy:person-detail', kwargs={'pk': self.unprivileged_person.id}),
            },
            # addition
            {
                'person': reverse('legacy:person-detail', kwargs={'pk': self.privileged_user.id}),
                'is_referent': False,
                'is_manager': True
            }
            # deletion: no membership for `self.manager`
        ])
        self.as_privileged(request)

        response = self.membership_bulk_view(request, parent_lookup_supportgroup=str(self.supportgroup.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        qs = self.supportgroup.memberships.all()

        self.assertEqual(len(qs), 2)
        self.assertCountEqual([membership.person_id for membership in qs], [self.unprivileged_person.id, self.privileged_user.id])
        self.assertCountEqual([membership.is_manager for membership in qs], [False, True])
        self.assertCountEqual([membership.is_referent for membership in qs], [False, False])
