from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from oauth2_provider.models import AbstractApplication

from ..lib.models import BaseAPIResource, AbstractLabel
from ..authentication.models import Role
from .scopes import scopes

__all__ = ["Client"]


class ClientManager(models.Manager):
    def get_by_natural_key(self, label):
        return self.select_related("role").get(label=label)

    def _create_client(
        self,
        client_id,
        password,
        *,
        is_superuser,
        is_active=True,
        oauth_enabled=None,
        trusted=None,
        **extra_fields
    ):
        """
        Creates and saves a client with the given client_id and password.
        """
        if not client_id:
            raise ValueError("Label must be set")

        if oauth_enabled is not None:
            extra_fields["authorization_grant_type"] = (
                "authorization-code" if oauth_enabled else "client-credentials"
            )

        if trusted is not None:
            extra_fields["skip_authorizations"] = trusted

        if password is not None:
            extra_fields["client_secret"] = password

        role = Role(
            type=Role.CLIENT_ROLE, is_superuser=is_superuser, is_active=is_active
        )

        with transaction.atomic():
            role.save()
            client = self.model(client_id=client_id, role=role, **extra_fields)
            client.save(using=self._db)

        return client

    def create_client(self, client_id, password=None, **extra_fields):
        """
        Create a client
        :param client_id:
        :param password: optional password that may be used to connect to the API
        :param extra_fields: any other field
        :return:
        """
        extra_fields.setdefault("is_superuser", False)
        return self._create_client(client_id, password, **extra_fields)

    def create_superclient(self, client_id, password, **extra_fields):
        """
        Create a super client
        :param label:
        :param password:
        :param extra_fields:
        :return:
        """
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_client(client_id, password, **extra_fields)


class Client(BaseAPIResource, AbstractApplication):
    objects = ClientManager()

    role = models.OneToOneField(
        "authentication.Role",
        on_delete=models.PROTECT,
        related_name="client",
        null=False,
    )

    description = models.TextField(
        _("description du client"),
        blank=True,
        help_text=_(
            "Une description du client à l'intention des utilisateurs éventuels."
        ),
    )

    contact_email = models.EmailField(
        _("email de contact"),
        blank=True,
        help_text=_("Une adresse email de contact pour ce client."),
    )

    scopes = ArrayField(
        models.CharField(
            max_length=255,
            choices=[(scope.name, scope.description) for scope in scopes],
        ),
        help_text=_("La liste des scopes autorisés pour ce client."),
        blank=True,
        default=list,
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ("name",)
        default_permissions = ("add", "change", "delete", "view")

    def __str__(self):
        return self.name

    # for retro-compat
    @property
    def label(self):
        return self.client_id

    def get_short_name(self):
        return self.label

    def get_full_name(self):
        return self.name
