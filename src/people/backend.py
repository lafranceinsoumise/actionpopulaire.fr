from django.contrib.auth.backends import ModelBackend

from authentication.models import Role
from .models import Person


class PersonBackend(object):
    """
    Authenticates persons
    """

    def authenticate(self, request, email=None, password=None):
        try:
            role = Role._default_manager.select_related('person').get(person__emails__address=email)
        except Role.DoesNotExist:
            Role().set_password(password)
        else:
            if role.check_password(password) and self.user_can_authenticate(role):
                return role

    def user_can_authenticate(self, role):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(role, 'is_active', None)
        return is_active or is_active is None


    def get_user(self, user_id):
        try:
            return Role.objects.select_related('person').get(pk=user_id)
        except Role.DoesNotExist:
            return None
