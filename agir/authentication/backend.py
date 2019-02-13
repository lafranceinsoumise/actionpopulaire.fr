from django.core.exceptions import ValidationError

from agir.authentication.crypto import connection_token_generator, short_code_generator
from agir.people.models import Person
from agir.authentication.backend_mixins import GetRoleMixin

from .models import Role


class ShortCodeBackend(GetRoleMixin):
    prefetch = ["person"]

    def authenticate(self, request, user_pk=None, short_code=None):
        if user_pk and short_code:
            if short_code_generator.check_short_code(user_pk, short_code):
                try:
                    role = Role.objects.select_related("person").get(person__pk=user_pk)
                except (Person.DoesNotExist, ValidationError):
                    return None

                if self.user_can_authenticate(role):
                    return role

        return None


class MailLinkBackend(GetRoleMixin):
    prefetch = ["person"]

    def authenticate(self, request, user_pk=None, token=None):
        if user_pk and token:
            try:
                person = Person.objects.select_related("role").get(pk=user_pk)
            except (Person.DoesNotExist, ValidationError):
                return None
            if connection_token_generator.check_token(
                token, user=person
            ) and self.user_can_authenticate(person.role):
                return person.role

        return None


class OAuth2Backend(GetRoleMixin):
    """Legacy backend, use to preserve current connection from people."""

    prefetch = ["person"]

    def authenticate(self, request):
        return None
