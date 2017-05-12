from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import empty
from django_countries.serializer_fields import CountryField


class LegacyBaseAPISerializer(serializers.ModelSerializer):
    """
    A legacy serializer that handles id fields (both internal and nationbuilder) and creation/modification time fields
    """
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
        allow_null=True,
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


class RelatedLabelField(serializers.SlugRelatedField):
    def __init__(self, slug_field=None, **kwargs):
        if slug_field is None:
            slug_field = 'label'

        super().__init__(slug_field, **kwargs)

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail('invalid')


class NestedContactSerializer(serializers.Serializer):
    name = serializers.CharField(
        label=_('Nom du contact'),
        required=False,
        allow_blank=True,
        max_length=255,
        source='contact_name',
    )

    email = serializers.EmailField(
        label=_('Adresse email du contact'),
        required=False,
        allow_blank=True,
        source='contact_email'
    )

    phone = serializers.CharField(
        label=_('Numéro de téléphone du contact'),
        required=False,
        allow_blank=True,
        max_length=30,
        source='contact_phone'
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.setdefault('source', '*')
        super().__init__(instance, data, **kwargs)


class NestedLocationSerializer(serializers.Serializer):
    name = serializers.CharField(
        label=_("nom du lieu"),
        max_length=255,
        required=False,
        allow_blank=True,
        source='location_name',
    )
    address = serializers.CharField(
        label=_('adresse complète'),
        max_length=255,
        required=False,
        allow_blank=True,
        source='location_address',
    )
    address1 = serializers.CharField(
        label=_("adresse (1ère ligne)"),
        max_length=100,
        required=False,
        allow_blank=True,
        source='location_address1',
    )
    address2 = serializers.CharField(
        label=_("adresse (2ème ligne)"),
        max_length=100,
        required=False,
        allow_blank=True,
        source='location_address2',
    )
    city = serializers.CharField(
        label=_("ville"),
        max_length=100,
        required=False,
        allow_blank=True,
        source='location_city',
    )
    zip = serializers.CharField(
        label=_("code postal"),
        max_length=20,
        required=False,
        allow_blank=True,
        source='location_zip',
    )
    state = serializers.CharField(
        label=_('état'),
        max_length=40,
        required=False,
        allow_blank=True,
        source='location_state',
    )

    country_code = CountryField(
        label=_('pays'),
        required=False,
        source='location_country'
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.setdefault('source', '*')
        super().__init__(instance, data, **kwargs)


class LegacyLocationMixin(serializers.ModelSerializer):
    location = NestedLocationSerializer(
        label=_('Lieu'),
        required=False,
    )

    @staticmethod
    def _flatten_location(validated_data):
        if 'location' in validated_data:
            field_content = validated_data.pop('location')

            for key, value in field_content.items():
                validated_data[key] = value

        return validated_data

    def create(self, validated_data):
        return super(LegacyLocationMixin, self).create(self._flatten_location(validated_data))

    def update(self, instance, validated_data):
        return super(LegacyLocationMixin, self).update(instance, self._flatten_location(validated_data))


class LegacyContactMixin(serializers.ModelSerializer):
    contact = NestedContactSerializer(
        label=_('Informations du contact'),
        required=False,
    )

    @staticmethod
    def _flatten_contact(validated_data):
        if 'contact' in validated_data:
            field_content = validated_data.pop('contact')

            for key, value in field_content.items():
                validated_data[key] = value

        return validated_data

    def create(self, validated_data):
        return super(LegacyContactMixin, self).create(self._flatten_contact(validated_data))

    def update(self, instance, validated_data):
        return super(LegacyContactMixin, self).update(instance, self._flatten_contact(validated_data))


class LegacyLocationAndContactMixin(LegacyLocationMixin, LegacyContactMixin, ):
    pass
