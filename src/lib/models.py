import uuid
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe, escape, format_html, format_html_join
from django_countries.fields import CountryField
from model_utils.models import TimeStampedModel


class UUIDIdentified(models.Model):
    """
    Mixin that replaces the default id by an UUID
    """
    id = models.UUIDField(
        _('UUID'),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("UUID interne à l'API pour identifier la ressource")
    )

    class Meta:
        abstract = True


class NationBuilderResource(models.Model):
    """
    Mixin that add a `nb_id` field that can store the id of the corresponding resource on NationBuilder
    """
    nb_id = models.IntegerField(
        _('ID sur NationBuilder'),
        null=True,
        blank=True,
        unique=True,
        help_text=_("L'identifiant de la ressource correspondante sur NationBuilder, si importé.")
    )

    class Meta:
        abstract = True


class BaseAPIResource(UUIDIdentified, TimeStampedModel):
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
    coordinates = models.PointField(_('coordonnées'), geography=True, null=True, blank=True, spatial_index=True)

    location_name = models.CharField(_("nom du lieu"), max_length=255, blank=True)
    location_address = models.CharField(_('adresse complète'), max_length=255, blank=True)
    location_address1 = models.CharField(_("adresse (1ère ligne)"), max_length=100, blank=True)
    location_address2 = models.CharField(_("adresse (2ème ligne)"), max_length=100, blank=True)
    location_city = models.CharField(_("ville"), max_length=100, blank=True)
    location_zip = models.CharField(_("code postal"), max_length=20, blank=True)
    location_state = models.CharField(_('état'), max_length=40, blank=True)
    location_country = CountryField(_('pays'), blank=True, blank_label=_('(sélectionner un pays)'))

    def html_full_address(self):
        res = []
        for f in ['location_name', 'location_address1', 'location_address2', 'location_state']:
            val = getattr(self, f, None)
            if val:
                res.append(val)

        if self.location_zip and self.location_city:
            res.append('{} {}'.format(self.location_zip, self.location_city))
        else:
            if self.location_zip:
                res.append(self.location_zip)
            if self.location_city:
                res.append(self.location_city)

        if self.location_country and str(self.location_country) != 'FR':
            res.append(self.location_country.name)

        return mark_safe('<br/>'.join(escape(line) for line in res))

    @property
    def short_address(self):
        attrs = ['location_address1', 'location_address2', 'location_zip', 'location_city']

        if self.location_country != 'FR':
            attrs.extend(['location_state', 'location_country'])

        return ', '.join(getattr(self, attr) for attr in attrs if getattr(self, attr))

    class Meta:
        abstract = True


class ContactMixin(models.Model):
    """
    Mixin that adds contact fields
    """
    contact_name = models.CharField(_('nom du contact'), max_length=255, blank=True)
    contact_email = models.EmailField(_('adresse email du contact'), blank=True)
    contact_phone = models.CharField(_('numéro de téléphone du contact'), max_length=30, blank=True)
    contact_hide_phone = models.BooleanField(_('Cacher mon numéro de téléphone'), default=False)

    def html_full_contact(self):
        parts = []

        if self.contact_name and self.contact_email:
            parts.append(format_html(
                '{name} &lt;<a href="mailto:{email}">{email}</a>&gt;',
                name=self.contact_name,
                email=self.contact_email
            ))
        elif self.contact_name:
            parts.append(self.contact_name)
        elif self.contact_email:
            parts.append(format_html('<a href="mailto:{email}">{email}</a>'))

        if self.contact_phone and not self.contact_hide_phone:
            parts.append(self.contact_phone)

        if parts:
            return format_html_join(mark_safe(" &mdash; "), '{}', ((part,) for part in parts))
        else:
            return format_html("<em>{}</em>", _("Pas d'informations de contact"))

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

    label = models.CharField(_('nom'), max_length=50, unique=True, blank=False)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.label
