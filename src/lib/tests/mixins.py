from clients import scopes
from clients.models import Client
from events.models import Event, Calendar
from groups.models import SupportGroup, Membership
from people.models import Person

PASSWORD = 'incredible password'


def load_fake_data():
    clients = {
        'api_front': Client.objects.create_client(
            'api_front',
            password=PASSWORD,
            oauth_enabled=True,
            uris=['http://localhost:8000/authentification/retour/'],
            scopes=[scopes.view_profile]
        ),
        'oauth': Client.objects.create_client(
            'oauth',
            password=PASSWORD,
            scopes=[scopes.view_profile]
        ),
    }

    people = {
        'admin': Person.objects.create_superperson('admin@example.com', PASSWORD),
        'user1': Person.objects.create_person('user1@example.com', PASSWORD),
        'user2': Person.objects.create_person('user2@example.com', PASSWORD),
    }

    # Groups

    groups = {
        'user1_group': SupportGroup.objects.create(name='Groupe géré par user1'),
        'user2_group': SupportGroup.objects.create(name='Groupe géré par user2')
    }
    Membership.objects.create(supportgroup=groups['user1_group'], person=people['user1'], is_manager=True, is_referent=True)
    Membership.objects.create(supportgroup=groups['user2_group'], person=people['user2'], is_manager=True, is_referent=True)
    Membership.objects.create(supportgroup=groups['user1_group'], person=people['user2'])

    return {
        'clients': clients,
        'people': people,
        'groups': groups,
    }



class FakeDataMixin():
    def setUp(self):
        self.data = load_fake_data()
        super().setUp()