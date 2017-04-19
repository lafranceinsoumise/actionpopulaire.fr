from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from model_utils.models import TimeStampedModel

from lib.models import BaseAPIResource, AbstractLabel


class ClientManager(models.Manager):
    def get_by_natural_key(self, label):
        return self.get(label=label)


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

    USERNAME_FIELD = 'name'

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
