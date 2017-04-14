from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.postgres.fields import ArrayField
from model_utils.models import TimeStampedModel

from lib.models import BaseAPIResource, AbstractLabel


class Client(BaseAPIResource, AbstractBaseUser):
    name = models.CharField(
        _('identifiant du client'),
        max_length=40,
        blank=False,
        unique=True,
        help_text=_("L'identifiant du client, utilisé pour l'authentication.")
    )

    uris = ArrayField(
        models.CharField(max_length=150, blank=False),
        verbose_name=_('URIs de redirection OAuth'),
        default=list,
        size=4
    )

    USERNAME_FIELD = 'name'


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
