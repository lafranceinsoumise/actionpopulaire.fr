from django.contrib.auth.backends import ModelBackend

from authentication.models import Role
from .models import Person


class PersonBackend(object):
    """
    Authenticates persons
    """

    def authenticate(self, request, email=None, password=None):
        try:
            person = Person._default_manager.get_by_natural_key(email)
        except Person.DoesNotExist:
            Role().set_password(password)
        else:
            if person.role.check_password(password) and self.user_can_authenticate(person.role):
                return person

    def user_can_authenticate(self, role):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(role, 'is_active', None)
        return is_active or is_active is None
