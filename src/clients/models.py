from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import Permission, Group
from django.contrib.postgres.fields import ArrayField
from model_utils.models import TimeStampedModel

from lib.models import BaseAPIResource, AbstractLabel


class ClientManager(models.Manager):
    def get_by_natural_key(self, label):
        return self.get(label=label)

    def _create_client(self, label, password, **extra_fields):
        """
        Creates and saves a client with the given label and password.
        """
        if not label:
            raise ValueError('Label must be set')
        client = self.model(label=label, **extra_fields)
        client.set_password(password)
        client.save(using=self._db)
        return client

    def create_client(self, label, password=None, **extra_fields):
        """
        Create a client 
        :param label: the user's email
        :param password: optional password that may be used to connect to the API
        :param extra_fields: any other field
        :return: 
        """
        extra_fields.setdefault('is_superuser', False)
        return self._create_client(label, password, **extra_fields)

    def create_superclient(self, label, password, **extra_fields):
        """
        Create a super client
        :param label: 
        :param password: 
        :param extra_fields: 
        :return: 
        """
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_client(label, password, **extra_fields)


class Client(BaseAPIResource, AbstractBaseUser):
    objects = ClientManager()

    label = models.CharField(
        _('identifiant du client'),
        max_length=40,
        blank=False,
        unique=True,
        help_text=_("L'identifiant du client, utilisé pour l'authentication.")
    )

    verbose_name = models.CharField(
        _('nom du client'),
        max_length=150,
        blank=False,
        help_text=_("Le nom du client, tel qu'affiché à l'utilisateur lorsqu'il autorise ce client.")
    )

    trusted = models.BooleanField(
        _('client de confiance'),
        default=False,
        help_text=_("Indique si ce client est de confiance : s'il l'est, l'utilisateur n'a pas besoin de "
                    "valider l'autorisation lors de la procédure OAuth.")
    )

    uris = ArrayField(
        models.CharField(max_length=150, blank=False),
        verbose_name=_('URIs de redirection OAuth'),
        default=list,
        size=4,
        help_text=_("La liste des URIs auxquelles le serveur d'authentification acceptera de rediriger les "
                    "utilisateurs pendant la procédure OAuth.")
    )

    scopes = models.ManyToManyField(
        'Scope',
        related_name='clients',
        blank=True,
        help_text=_('La liste des scopes autorisés pour ce client.')
    )

    # same fields as in PermissionsMixins
    is_superuser = models.BooleanField(
        _('superuser status'),
        default=False,
        help_text=_(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="client_set",
        related_query_name="client",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="client_set",
        related_query_name="client",
    )

    USERNAME_FIELD = 'label'

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ('label',)
        default_permissions = ('add', 'change', 'delete', 'view')


class Scope(AbstractLabel):
    class Meta:
        verbose_name = _('scope')
        verbose_name_plural = _('scopes')


class Authorization(TimeStampedModel):
    person = models.ForeignKey('people.Person', related_name='authorizations')
    client = models.ForeignKey('Client', related_name='authorizations')
    scopes = models.ManyToManyField('Scope', related_name='authorizations')

    class Meta:
        verbose_name = 'autorisation',
        verbose_name_plural = 'autorisations'
        unique_together = ('person', 'client')
