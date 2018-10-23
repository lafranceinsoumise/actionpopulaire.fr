import uuid
import os
from django.contrib.gis.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe, format_html, format_html_join
from django_countries.fields import CountryField
from django.conf import settings
from django.contrib.postgres.fields import JSONField

from model_utils.models import TimeStampedModel
from stdimage.models import StdImageField
from stdimage.utils import UploadTo

from .form_fields import RichEditorWidget
from .html import sanitize_html
from .display import display_address


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
        help_text=_("Comment les coordonnées ci-dessus ont-elle été acquises")
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
        return display_address(self)

    def short_location(self):
        local_part = self.location_name
        if self.location_country == 'FR':
            city_part = self.location_city
        elif self.location_city:
            city_part = self.location_city + ', ' + self.location_country.name
        elif self.location_country:
            city_part = self.location_country.name
        else:
            city_part = ""

        if local_part and city_part:
            return '{} ({})'.format(local_part, city_part)
        else:
            return local_part or city_part or _('Pas de localisation')

    @property
    def short_address(self):
        attrs = ['location_address1', 'location_address2', 'location_zip', 'location_city']

        if self.location_country != 'FR':
            attrs.extend(['location_state', 'location_country'])

        return ', '.join(str(getattr(self, attr)) for attr in attrs if getattr(self, attr))

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


class UploadToInstanceDirectoryWithFilename(UploadTo):
    def __init__(self, filename):
        # make sure it will be correctly deconstructed
        super().__init__(filename=filename)
        self.filename = filename

    def __call__(self, instance, filename):
        _, ext = os.path.splitext(filename)

        return os.path.join(
            instance.__class__.__name__,
            str(instance.pk),
            "{}{}".format(self.filename, ext)
        )


class UploadToRelatedObjectDirectoryWithUUID(UploadTo):
    def __init__(self, related):
        # make sure it will be correctly deconstructed
        super().__init__(related=related)
        self.related = related

    def __call__(self, instance, filename):
        _, ext = os.path.splitext(filename)
        related_object = getattr(instance, self.related)

        return os.path.join(
            related_object.__class__.__name__,
            str(related_object.pk),
            "{}{}".format(str(uuid.uuid4()), ext)
        )


class AbstractMapObjectLabel(TimeStampedModel, AbstractLabel):
    """
    Abstract class for event and group labels which should have special appearance on map
    """
    VISIBILITY_NONE = 'N'
    VISIBILITY_ADMIN = 'D'
    VISIBILITY_ALL = 'A'
    VISIBILITY_CHOICES = (
        (VISIBILITY_NONE, _('Personne (plus utilisé)')),
        (VISIBILITY_ADMIN, _("Seulement depuis l'administration")),
        (VISIBILITY_ALL, _("N'importe qui"))
    )

    visibility = models.CharField(_('Qui peut créer avec ce sous-type ?'), default=VISIBILITY_ADMIN, max_length=1,
                                  choices=VISIBILITY_CHOICES)
    hide_text_label = models.BooleanField(_('cacher le label texte'), default=False)

    icon = models.ImageField(
        verbose_name=_('icon'),
        upload_to=UploadToInstanceDirectoryWithFilename('icon'),
        help_text=_("L'icône associée aux marqueurs sur la carte."),
        blank=True,
    )

    icon_name = models.CharField(_("Nom de l'icône Font Awesome"), max_length=200, blank=True)

    color = models.CharField(
        _("couleur"),
        max_length=7,
        validators=[RegexValidator(regex='^#[0-9A-Fa-f]{6}$')],
        help_text=_('La couleur associée aux marqueurs sur la carte.'),
        blank=True,
    )

    icon_anchor_x = models.PositiveSmallIntegerField(_("ancre de l'icône (x)"), blank=True, null=True)
    icon_anchor_y = models.PositiveSmallIntegerField(_("ancre de l'icône (y)"), blank=True, null=True)
    popup_anchor_y = models.PositiveSmallIntegerField(_("placement de la popup (par rapport au point)"), blank=True, null=True)

    config = JSONField(_('Configuration'), default=dict)

    class Meta:
        abstract = True


class ImageMixin(models.Model):
    image = StdImageField(
        _("image"),
        upload_to=UploadToInstanceDirectoryWithFilename('banner'),
        variations={
            'thumbnail': (400, 250),
            'banner': (1200, 400),
        },
        blank=True,
        help_text=_("Vous pouvez ajouter une image de bannière : elle apparaîtra sur la page, et sur les réseaux"
                    " sociaux en cas de partage. Préférez une image à peu près deux fois plus large que haute. Elle doit"
                    " faire au minimum 1200 pixels de large et 630 de haut pour une qualité optimale.")
    )

    class Meta:
        abstract = True


class DescriptionField(models.TextField):
    def __init__(self, *args, allowed_tags=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._allowed_tags = allowed_tags

    def formfield(self, **kwargs):
        defaults = {'widget': RichEditorWidget(attrs=kwargs.get('attrs', {}))}
        defaults.update(kwargs)
        return super().formfield(**defaults)

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)

        allowed_tags = self._allowed_tags

        def html_FIELD(self, tags=None):
            if tags is None:
                if isinstance(allowed_tags, str):
                    tags = getattr(self, allowed_tags)
                else:
                    tags = allowed_tags

            if tags is None:
                raise TypeError('Cannot call html_{0} without a tags argument if no default was set on field {0} creation'.format(name))

            if callable(tags):
                tags = tags()

            if not isinstance(tags, list):
                tags = list(tags)

            return sanitize_html(getattr(self, name), tags)

        setattr(cls, 'html_{}'.format(name), html_FIELD)


class DescriptionMixin(models.Model):
    description = DescriptionField(
        _('description'),
        blank=True,
        help_text=_("Une courte description"),
        allowed_tags='allowed_tags'
    )

    allow_html = models.BooleanField(
        _("autoriser le HTML étendu dans la description"),
        default=False,
    )

    class Meta:
        abstract = True

    def allowed_tags(self):
        if self.allow_html: return settings.ADMIN_ALLOWED_TAGS
        else: return settings.USER_ALLOWED_TAGS
