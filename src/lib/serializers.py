from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from django_countries.serializer_fields import CountryField

from . import validators


class LegacyBaseAPISerializer(serializers.ModelSerializer):
    _id = serializers.UUIDField(
        label=_('UUID'),
        source='id',
        read_only=True,
        help_text=_("UUID interne à l'API pour identifier la ressource")
    )

    id = serializers.IntegerField(
        label=_('ID sur NationBuilder'),
        source='nb_id',
        required=False,
        help_text=_("L'identifiant de la ressource correspondante sur NationBuilder, si importé.")
    )

    _created = serializers.DateTimeField(
        label=_('Créé le'),
        source='created',
        read_only=True,
        help_text=_('Date de création de la ressource')
    )

    _updated = serializers.DateTimeField(
        label=_('Mise à jour le'),
        source='modified',
        read_only=True,
        help_text=_('Date de mise à jour de la ressource')
    )
