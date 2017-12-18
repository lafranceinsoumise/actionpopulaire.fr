from datetime import timedelta

from django.contrib.auth.models import Group
from django.utils import timezone

from clients import scopes
from clients.models import Client
from events.models import Calendar, Event, OrganizerConfig, RSVP
from groups.models import SupportGroup, Membership
from people.models import Person

PASSWORD = 'incredible password'

LOREM_IPSUM = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore
et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
'''

def load_fake_data():
    clients = {
        'api_front': Client.objects.create_client(
            'api_front',
            password=PASSWORD,
            oauth_enabled=True,
            uris=['http://localhost:8000/authentification/retour/'],
            scopes=['view_profile']
        ),
        'oauth': Client.objects.create_client(
            'oauth',
            password=PASSWORD,
            scopes=['view_profil']
        ),
    }
    clients['oauth'].role.groups.add(Group.objects.get(name='oauth_providers'))

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

    # Events
    calendars = {
        'evenements_locaux': Calendar.objects.create_calendar('Évènements locaux', slug='calendar', user_contributed=True),
        'national': Calendar.objects.create_calendar('National', slug='national')
    }

    events = {
        'user1_event1': Event.objects.create(
            name='Événement créé par user1',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            calendar=calendars['evenements_locaux'],
        ),
        'user1_event2': Event.objects.create(
            name='Autre événement créé par user1 sans personne dedans',
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            calendar=calendars['evenements_locaux'],
        ),
        'user1_past_event': Event.objects.create(
            name='Événement passé créé par user1',
            start_time=timezone.now() + timedelta(days=-1),
            end_time=timezone.now() + timedelta(days=-1, hours=1),
            calendar=calendars['evenements_locaux'],
            report_content=LOREM_IPSUM
        ),
        'user1_unpublished_event': Event.objects.create(
            name='Évenement non publié créé par user1',
            published=False,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            calendar=calendars['evenements_locaux'],
        )
    }
    [OrganizerConfig.objects.create(
        event=event,
        person=people['user1'],
        is_creator=True,
        as_group=groups['user1_group']
    ) for event in [events['user1_event1'], events['user1_event2'], events['user1_past_event'], events['user1_unpublished_event']]]
    [RSVP.objects.create(person=user, event=events['user1_event1']) for user in [people['user1'], people['user2']]]
    [RSVP.objects.create(person=user, event=events['user1_past_event']) for user in [people['user1'], people['user2']]]
    [RSVP.objects.create(person=user, event=events['user1_unpublished_event']) for user in [people['user1'], people['user2']]]

    return {
        'clients': clients,
        'people': people,
        'groups': groups,
        'events': events,
    }



class FakeDataMixin():
    def setUp(self):
        self.data = load_fake_data()
        super().setUp()