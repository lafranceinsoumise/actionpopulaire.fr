from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django_countries.serializer_fields import CountryField
from phonenumber_field.phonenumber import to_python
from rest_framework import serializers, exceptions
from rest_framework.fields import empty
from rest_framework.serializers import BaseSerializer
from rest_framework_gis.fields import GeometryField

from agir.lib.geo import get_commune
from agir.carte.models import StaticMapImage
from .data import code_postal_vers_code_departement
from .geo import FRENCH_COUNTRY_CODES
from .tasks import create_static_map_image_from_coordinates


class NullAsBlankMixin:
    """Field mixin that makes a null input be interpreted as the empty string instead.

    This field is used to accept null values for char fields and still follow
    Django convention of not using NULL values for text fields and to use the empty
    string for "no data".

    See: https://docs.djangoproject.com/en/1.11/ref/models/fields/#null

    """

    def get_value(self, dictionary):
        value = super(NullAsBlankMixin, self).get_value(dictionary)
        if value is None:
            return ""
        return value


class NullableCharField(NullAsBlankMixin, serializers.CharField):
    """CharField that interprets a `null` input as the empty string."""

    def __init__(self, **kwargs):
        kwargs.setdefault("allow_blank", True)
        super(NullableCharField, self).__init__(**kwargs)


class NullableCountryField(NullAsBlankMixin, CountryField):
    """CharField that interprets a `null` input as the empty string."""

    pass


class SimpleLocationSerializer(serializers.Serializer):
    ADDRESS_FIELDS = (
        "name",
        "address1",
        "address2",
        "address",
        "shortAddress",
    )

    name = serializers.CharField(source="location_name")
    address1 = serializers.CharField(source="location_address1")
    address2 = serializers.CharField(
        source="location_address2", required=False, allow_blank=True
    )
    zip = serializers.CharField(source="location_zip")
    city = serializers.CharField(source="location_city")
    departement = serializers.SerializerMethodField(read_only=True)
    country = CountryField(source="location_country")
    address = serializers.SerializerMethodField()
    commune = serializers.SerializerMethodField(read_only=True)

    shortAddress = serializers.CharField(source="short_address", required=False)
    shortLocation = serializers.CharField(source="short_location", required=False)

    def __init__(self, *args, with_address=True, **kwargs):
        if not with_address:
            for field in self.ADDRESS_FIELDS:
                del self.fields[field]

        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        if not data["zip"] and not data["city"]:
            return None
        return data

    def get_commune(self, obj):
        commune = get_commune(obj)
        if commune is not None:
            commune = {
                "name": commune.nom_complet,
                "nameOf": commune.nom_avec_charniere,
            }
        return commune

    def get_departement(self, obj):
        if hasattr(obj, "get_departement"):
            return obj.get_departement()
        if hasattr(obj, "departement"):
            return obj.departement
        if obj.location_zip:
            return code_postal_vers_code_departement(obj.location_zip)
        return None

    def get_address(self, obj):
        parts = [
            obj.location_address1,
            obj.location_address2,
            f"{obj.location_zip} {obj.location_city}".strip(),
        ]

        if obj.location_country and obj.location_country != "FR":
            parts.append(obj.location_country.name)

        return "\n".join(p for p in parts if p)


class LocationSerializer(SimpleLocationSerializer):
    coordinates = GeometryField(required=False)
    staticMapUrl = serializers.SerializerMethodField(read_only=True)

    def get_staticMapUrl(self, obj):
        if hasattr(obj, "static_map_image") and obj.static_map_image:
            return StaticMapImage(image=obj.static_map_image).image.url

        if obj.coordinates is None:
            return ""

        static_map_image = StaticMapImage.objects.filter(
            center__dwithin=(
                obj.coordinates,
                StaticMapImage.UNIQUE_CENTER_MAX_DISTANCE,
            ),
        ).first()

        if static_map_image is None:
            create_static_map_image_from_coordinates.delay(
                [obj.coordinates[0], obj.coordinates[1]]
            )
            return ""

        return static_map_image.image.url


class RelatedLabelField(serializers.SlugRelatedField):
    """A related field that shows a slug and can be used to create a new related model object"""

    def __init__(self, slug_field=None, **kwargs):
        if slug_field is None:
            slug_field = "label"

        super().__init__(slug_field, **kwargs)

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except (TypeError, ValueError):
            self.fail("invalid")


class ExistingRelatedLabelField(RelatedLabelField):
    def __init__(self, slug_field=None, **kwargs):
        super().__init__(slug_field, **kwargs)

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(**{self.slug_field: data})
        except (TypeError, ValueError, ObjectDoesNotExist):
            self.fail("invalid")


class PhoneField(serializers.CharField):
    region = "FR"
    default_error_messages = {
        "invalid_format": "Saisissez un numéro de téléphone français valide ou un numéro avec un indicatif "
        "international."
    }

    def to_internal_value(self, value):
        phone_number = super().to_internal_value(value)
        phone_number = to_python(phone_number, region=self.region)
        if not phone_number:
            return ""

        if phone_number.is_valid():
            return str(phone_number)

        if self.region == "FR":
            for country_code in FRENCH_COUNTRY_CODES:
                phone_number = to_python(value, country_code)
                if phone_number.is_valid():
                    return str(phone_number)

        self.fail("invalid_format")


class NestedContactSerializer(serializers.Serializer):
    """A nested serializer for the fields defined by :py:class:`lib.models.ContactMixin`"""

    name = serializers.CharField(
        label="Nom du contact",
        required=True,
        max_length=255,
        source="contact_name",
    )

    email = serializers.EmailField(
        label="Adresse email du contact",
        required=True,
        allow_blank=True,
        source="contact_email",
    )

    phone = PhoneField(
        label="Numéro de téléphone du contact",
        required=True,
        max_length=30,
        source="contact_phone",
    )

    hidePhone = serializers.BooleanField(
        label="Ne pas rendre le numéro de téléphone public",
        required=False,
        default=False,
        source="contact_hide_phone",
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.setdefault("source", "*")
        super().__init__(instance, data, **kwargs)


class NestedLocationSerializer(serializers.Serializer):
    """A nested serializer for the fields defined by :py:class:`lib.models.LocationMixin`

    All these fields will be collected and serialized as a a JSON object.
    """

    name = NullableCharField(
        label="nom du lieu",
        max_length=255,
        required=True,
        source="location_name",
    )
    address = NullableCharField(
        label="adresse complète",
        max_length=255,
        required=False,
        source="location_address",
    )
    address1 = NullableCharField(
        label="adresse (1ère ligne)",
        max_length=100,
        required=True,
        source="location_address1",
    )
    address2 = NullableCharField(
        label="adresse (2ème ligne)",
        max_length=100,
        required=False,
        source="location_address2",
    )
    city = NullableCharField(
        label="ville", max_length=100, required=True, source="location_city"
    )
    zip = NullableCharField(
        label="code postal", max_length=20, required=True, source="location_zip"
    )
    state = NullableCharField(
        label="état", max_length=40, required=False, source="location_state"
    )
    country = NullableCountryField(
        label="pays", required=True, source="location_country"
    )

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.setdefault("source", "*")
        super().__init__(instance, data, **kwargs)


class UpdatableListSerializer(serializers.ListSerializer):
    matching_attr = None

    def get_additional_fields(self):
        return {}

    def update(self, instances, validated_data):
        instance_mapping = {
            getattr(instance, self.matching_attr): instance for instance in instances
        }
        try:
            data_mapping = {item[self.matching_attr]: item for item in validated_data}
        except KeyError:
            raise exceptions.ValidationError(
                _("Données invalides en entrée"), code="invalid_data"
            )

        ret = []

        additional_fields = self.get_additional_fields()

        for matching_value, data in data_mapping.items():
            instance = instance_mapping.get(matching_value, None)

            # add additional field to data before saving it
            data.update(additional_fields)

            if instance is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(instance, data))

        for matching_value, instance in instance_mapping.items():
            if matching_value not in data_mapping:
                instance.delete()

        return ret


class ContactMixinSerializer(serializers.Serializer):
    name = serializers.CharField(source="contact_name")
    # email = serializers.CharField(source="contact_email")
    # phone = serializers.SerializerMethodField(source="contact_phone")
    email = serializers.ReadOnlyField(default=None)
    phone = serializers.ReadOnlyField(default=None)

    def get_phone(self, obj):
        if obj.contact_hide_phone:
            return None
        return obj.contact_phone

    def to_representation(self, instance):
        data = super().to_representation(instance=instance)
        if all(not v for v in data.values()):
            return None
        return data


class FlexibleFieldsMixin(BaseSerializer):
    def __init__(self, instance=None, data=empty, fields=None, **kwargs):
        super().__init__(instance=instance, data=data, **kwargs)

        if fields is not None:
            for f in set(self.fields).difference(fields):
                del self.fields[f]


class CurrentPersonDefault:
    """
    May be applied as a `default=...` value on a serializer field.
    Returns the current user's person.
    """

    requires_context = True

    def __call__(self, serializer_field):
        user = serializer_field.context["request"].user
        if user is None or user.is_anonymous or not user.person:
            return None

        return user.person


class CurrentPersonField(serializers.HiddenField):
    """
    A hidden field that does not take input from the user,
    and does not present any output,
    but it does populate a field in `validated_data`,
    based on the current authenticated user person instance.
    """

    default = CurrentPersonDefault()

    def __init__(self, **kwargs):
        kwargs["default"] = self.default
        super().__init__(**kwargs)
