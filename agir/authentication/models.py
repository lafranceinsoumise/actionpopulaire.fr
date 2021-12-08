import uuid
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin, _user_has_perm
from django.utils.crypto import salted_hmac
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django_prometheus.models import ExportModelOperationsMixin


__all__ = ["Role"]


class RoleManager(BaseUserManager):
    pass


class Role(ExportModelOperationsMixin("role"), PermissionsMixin, AbstractBaseUser):
    PERSON_ROLE = "P"
    CLIENT_ROLE = "C"

    ROLE_TYPE = [(PERSON_ROLE, _("Personne")), (CLIENT_ROLE, _("Client"))]

    objects = RoleManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    type = models.CharField(
        _("type de rôle"),
        max_length=1,
        choices=ROLE_TYPE,
        editable=False,
        blank=False,
        null=False,
    )

    USERNAME_FIELD = "id"

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    def __str__(self):
        if self.type == self.CLIENT_ROLE:
            try:
                return "Client role -> %r" % self.client
            except ObjectDoesNotExist:
                return "Unknown Client role %s" % self.pk
        elif self.type == self.PERSON_ROLE:
            try:
                return "Person role -> %r" % self.person
            except ObjectDoesNotExist:
                return "Unknown Person role %s" % self.pk
        else:
            return "Unknown role %s" % self.pk

    def __repr__(self):
        if self.type == self.PERSON_ROLE:
            related = {"attr": "person", "object": self.person}
        else:
            related = {"attr": "client", "object": self.client}

        return "{klass}(type={type!r}, {related}, is_staff={is_staff}, is_active={is_active})".format(
            klass=self.__class__.__name__,
            type=self.type,
            related="{attr}={object}".format(**related),
            is_staff=self.is_staff,
            is_active=self.is_active,
        )

    def has_perm(self, perm, obj=None):
        """
        Override PermissionsMixin has_perm to deactivate is_superuser if
        authenticated through a token
        """

        # Active superusers have all permissions.
        if self.is_active and self.is_superuser and not hasattr(self, "token"):
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def get_short_name(self):
        if self.type == self.PERSON_ROLE:
            return self.person.get_short_name()
        else:
            return self.client.get_short_name()

    def get_full_name(self):
        if self.type == self.PERSON_ROLE:
            return self.person.get_full_name()
        else:
            return self.client.get_full_name()

    def get_session_auth_hash(self):
        """
        Return an HMAC of the password field.
        """

        # utiliser le même salt pour ne pas invalider les sessions
        key_salt = "django.contrib.auth.models.AbstractBaseUser.get_session_auth_hash"

        to_hash = self.password

        if self.type == self.PERSON_ROLE and self.person:
            to_hash += self.person.auto_login_salt

        return salted_hmac(key_salt, to_hash).hexdigest()
