from django.db import models
from django.utils.translation import ugettext_lazy as _

from lib.models import (
    APIResource, AbstractLabel, NationBuilderResource, ContactMixin, LocationMixin
)


class SupportGroup(APIResource, LocationMixin, ContactMixin):
    """
    Model that represents a support group 
    """
    name = models.CharField(
        _("nom"),
        max_length=255,
        blank=False,
        help_text=_("Le nom du groupe d'appui"),
    )

    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_("Une description du groupe d'appui, en MarkDown"),
    )

    nb_path = models.CharField(_('NationBuilder path'), max_length=255, blank=True)

    tags = models.ManyToManyField('SupportGroupTag', related_name='events', blank=True)


class SupportGroupTag(AbstractLabel):
    pass
