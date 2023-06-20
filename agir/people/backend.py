from agir.authentication.backend_mixins import GetRoleMixin
from agir.authentication.models import Role


class PersonBackend(GetRoleMixin):
    """
    Authenticates persons
    """

    prefetch = ["person"]

    def authenticate(self, request, email=None, password=None):
        try:
            role = Role._default_manager.select_related("person").get(
                person__emails__address__iexact=email
            )
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
        is_active = getattr(role, "is_active", None)
        return is_active or is_active is None
