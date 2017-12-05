import uuid
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe, format_html, format_html_join
from django_countries.fields import CountryField
from django.conf import settings

import bleach

from model_utils.models import TimeStampedModel
from stdimage.models import StdImageField
from stdimage.utils import UploadToAutoSlugClassNameDir

from .form_fields import RichEditorWidget
from .html import sanitize_html


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
    COORDINATES_MANUAL = 0
    COORDINATES_EXACT = 10
    COORDINATES_STREET = 20
    COORDINATES_CITY = 30
    COORDINATES_UNKNOWN_PRECISION = 50
    COORDINATES_NOT_FOUND = 255
    COORDINATES_TYPE_CHOICES = (
        (COORDINATES_MANUAL, _("Coordonnées manuelles")),
        (COORDINATES_EXACT, _("Coordonnées automatiques précises")),
        (COORDINATES_STREET, _("Coordonnées automatiques approximatives (niveau rue)")),
        (COORDINATES_CITY, _("Coordonnées automatiques approximatives (ville)")),
        (COORDINATES_UNKNOWN_PRECISION, _("Coordonnées automatiques (qualité inconnue)")),
        (COORDINATES_NOT_FOUND, _("Coordonnées introuvables"))
    )

    GEOCODING_FIELDS = {
        'location_address1', 'location_address2', 'location_city', 'location_zip', 'location_state', 'location_country'
    }

    coordinates = models.PointField(_('coordonnées'), geography=True, null=True, blank=True, spatial_index=True)
    coordinates_type = models.PositiveSmallIntegerField(
        _("type de coordonnées"),
        choices=COORDINATES_TYPE_CHOICES,
        null=True,
        editable=False,
        help_text=_("Comment les coordonnées ci-dessus ont-elle été acquéries")
    )

    location_name = models.CharField(_('nom du lieu'), max_length=255, blank=True)
    location_address1 = models.CharField(_("adresse (1ère ligne)"), max_length=100, blank=True)
    location_address2 = models.CharField(_("adresse (2ème ligne)"), max_length=100, blank=True)
    location_city = models.CharField(_("ville"), max_length=100, blank=True)
    location_zip = models.CharField(_("code postal"), max_length=20, blank=True)
    location_state = models.CharField(_('état'), max_length=40, blank=True)
    location_country = CountryField(_('pays'), blank=True, blank_label=_('(sélectionner un pays)'))

    # legacy fields --> copied from NationBuilder
    location_address = models.CharField(
        _('adresse complète'),
        max_length=255,
        blank=True,
        help_text=_(
            "L'adresse telle qu'elle a éventuellement été copiée depuis NationBuilder. Ne plus utiliser."
        )
    )

    def html_full_address(self):
        parts = []
        if self.location_name:
            parts.append(format_html('<strong>{}</strong>', self.location_name))

        if self.location_address1:
            parts.append(self.location_address1)
            if self.location_address2:
                parts.append(self.location_address2)
        elif self.location_address:
            # use full address (copied from NationBuilder) only when we have no address1 field
            parts.append(self.location_address)

        if self.location_state:
            parts.append(self.location_state)

        if self.location_zip and self.location_city:
            parts.append('{} {}'.format(self.location_zip, self.location_city))
        else:
            if self.location_zip:
                parts.append(self.location_zip)
            if self.location_city:
                parts.append(self.location_city)

        if self.location_country and str(self.location_country) != 'FR':
            parts.append(self.location_country.name)

        return format_html_join(mark_safe('<br/>'), '{}', ((part,) for part in parts))

    @property
    def short_address(self):
        attrs = ['location_address1', 'location_address2', 'location_zip', 'location_city']

        if self.location_country != 'FR':
            attrs.extend(['location_state', 'location_country'])

        return ', '.join(getattr(self, attr) for attr in attrs if getattr(self, attr))

    def has_location(self):
        return self.coordinates is not None

    def has_manual_location(self):
        return self.coordinates_type == self.COORDINATES_MANUAL

    def has_automatic_location(self):
        return self.coordinates_type is not None and self.COORDINATES_MANUAL < self.coordinates_type < self.COORDINATES_NOT_FOUND

    def should_relocate_when_address_changed(self):
        return not self.has_location() or self.has_automatic_location()

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
            parts.append(format_html('<a href="mailto:{email}">{email}</a>', email=self.contact_email))

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


class ImageMixin(models.Model):
    image = StdImageField(
        _("image"),
        upload_to=UploadToAutoSlugClassNameDir(populate_from="name", path="banners"),
        variations={
            'thumbnail': (400, 250),
            'banner': (1200, 400),
        },
        blank=True,
        help_text=_("Vous pouvez ajouter une image de bannière : elle apparaîtra sur la page de votre événement, et sur"
                    " les réseaux sociaux si vous y partagez "
                    "L'image à utiliser pour l'affichage sur la page, comme miniature dans les lstes, et"
                    " pour le partage sur les réseaux sociaux. Elle doit faire au minimum 1200 pixels de large, et 630"
                    " de haut. Utilisez un format large, à peu près deux fois plus large que haut.")
    )

    class Meta:
        abstract = True


class DescriptionField(models.TextField):
    def formfield(self, **kwargs):
        defaults = {'widget': RichEditorWidget(attrs=kwargs.get('attrs', {}))}
        defaults.update(kwargs)
        return super().formfield(**defaults)


class DescriptionMixin(models.Model):
    description = DescriptionField(
        _('description'),
        blank=True,
        help_text=_("Une courte description"),
    )

    allow_html = models.BooleanField(
        _("autoriser le HTML étendu dans la description"),
        default=False,
    )

    class Meta:
        abstract = True

    def html_description(self):
        tags = settings.ADMIN_ALLOWED_TAGS if self.allow_html else settings.USER_ALLOWED_TAGS
        return sanitize_html(self.description, tags)
