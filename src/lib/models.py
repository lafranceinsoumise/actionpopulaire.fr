import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from model_utils.models import TimeStampedModel


class UUIDIdentified(models.Model):
    """
    Mixin that replaces the default id by an UUID
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    class Meta:
        abstract = True


class NationBuilderResource(models.Model):
    """
    Mixin that add a `nb_id` field that can store the id of the corresponding resource on NationBuilder
    """
    nb_id = models.IntegerField(_('identifiant sur NationBuilder'), null=True, unique=True)

    class Meta:
        abstract = True


class APIResource(UUIDIdentified, NationBuilderResource, TimeStampedModel):
    """
    Abstract base class for APIResource that also exist on NationBuilder
    
    Automatically add an UUID identifier, a NationBuilder id fields, and automatic
    timestamps on modification and creation
    """
    class Meta:
        abstract = True


class LocationMixin(models.Model):
    """
    Mixin that adds location fields
    """
    coordinates_lat = models.DecimalField(_('latitude géographique'), max_digits=9, decimal_places=6, null=True)
    coordinates_lon = models.DecimalField(_('longitude géographique'), max_digits=9, decimal_places=6, null=True)

    location_name = models.CharField(_("nom du lieu"), max_length=255, blank=True)
    location_address = models.CharField(_('adresse complète'), max_length=255, blank=True)
    location_address1 = models.CharField(_("adresse (1ère ligne)"), max_length=100, blank=True)
    location_address2 = models.CharField(_("adresse (2ème ligne)"), max_length=100, blank=True)
    location_city = models.CharField(_("ville"), max_length=100, blank=True)
    location_zip = models.CharField(_("code postal"), max_length=20, blank=True)
    location_state = models.CharField(_('état'), max_length=40, blank=True)
    location_country = CountryField(_('pays'), blank=True, blank_label=_('(sélectionner un pays'))

    class Meta:
        abstract = True


class ContactMixin(models.Model):
    """
    Mixin that adds contact fields
    """
    contact_name = models.CharField(_('nom du contact'), max_length=255, blank=True)
    contact_email = models.EmailField(_('adresse email du contact'), blank=True)
    contact_phone = models.CharField(_('numéro de téléphone du contact'), max_length=30, blank=True)

    class Meta:
        abstract = True


class AbstractLabelManager(models.Manager):
    def get_by_natural_key(self, label):
        return self.get(label=label)


class AbstractLabel(models.Model):
    """
    Abstract base class for all kinds of unique label (tags, categories, etc.)
    """
    objects = AbstractLabelManager()

    label = models.CharField(_('nom'), max_length=30, unique=True, blank=False)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.label
