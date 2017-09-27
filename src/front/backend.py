from django.urls import resolve
from urllib.parse import urlparse

from people.models import Person
from authentication.models import Role

class OAuth2Backend(object):
    def authenticate(self, profile_url=None):
        if profile_url:
            path = urlparse(profile_url).path.replace('/legacy', '')

            match = resolve(path, urlconf='api.routers')

            if match.view_name == 'person-detail':
                person_id = match.kwargs['pk']
                person = Person.objects.select_related('role').get(pk=person_id)

                return person.role

            # not authenticated
            return None

    def get_user(self, user_id):
        try:
            return Role.objects.select_related('person').get(pk=user_id)
        except Role.DoesNotExist:
            return None
