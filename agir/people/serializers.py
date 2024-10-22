from datetime import date
from functools import partial

from django.db import transaction
from django.http import Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_countries.serializer_fields import CountryField
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from agir.elus.models import MandatMunicipal, StatutMandat, types_elus
from agir.lib.data import french_zipcode_to_country_code, FRANCE_COUNTRY_CODES
from agir.lib.serializers import FlexibleFieldsMixin, PhoneField, CurrentPersonField
from agir.lib.utils import is_absolute_url
from . import models
from .actions.subscription import (
    SUBSCRIPTION_TYPE_LFI,
    SUBSCRIPTION_TYPE_CHOICES,
    subscription_success_redirect_url,
    save_subscription_information,
    SUBSCRIPTION_EMAIL_SENT_REDIRECT,
    save_contact_information,
)
from .models import Person, PersonTag
from .tags import media_tags
from .tasks import send_confirmation_email
from ..groups.models import SupportGroup
from ..lib.tasks import geocode_person
from ..lib.token_bucket import TokenBucket

person_fields = {f.name: f for f in models.Person._meta.get_fields()}
subscription_mail_bucket = TokenBucket("SubscriptionMail", 5, 600)


class PersonEmailSerializer(serializers.ModelSerializer):
    """Basic PersonEmail serializer used to show and edit PersonEmail"""

    def __init__(self, *args, **kwargs):
        serializers.ModelSerializer.__init__(self, *args, **kwargs)
        queryset = models.PersonEmail.objects.all()
        try:
            pk = self.context["view"].kwargs["pk"]
        except KeyError:
            pk = None
        if pk is not None:
            try:
                queryset = queryset.exclude(person__id=pk)
            except ValueError:
                queryset = queryset.exclude(person__nb_id=pk)

        self.fields["address"] = serializers.EmailField(
            max_length=254, validators=[UniqueValidator(queryset=queryset)]
        )

    bounced = serializers.BooleanField()

    class Meta:
        model = models.PersonEmail
        fields = ("address", "bounced", "bounced_date")


class PersonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonTag
        fields = ("url", "id", "label", "description")


class SubscriptionRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=SUBSCRIPTION_TYPE_CHOICES, default=SUBSCRIPTION_TYPE_LFI, required=False
    )

    email = serializers.EmailField(
        required=True,
    )
    location_zip = serializers.CharField(
        required=True,
    )
    location_city = serializers.CharField(required=False, allow_blank=True)
    location_country = CountryField(required=False, allow_blank=True)

    first_name = serializers.CharField(
        max_length=person_fields["first_name"].max_length,
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        max_length=person_fields["last_name"].max_length,
        required=False,
        allow_blank=True,
    )
    contact_phone = PhoneNumberField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False)
    gender = serializers.ChoiceField(
        choices=Person.GENDER_CHOICES,
        required=False,
    )
    media_preferences = serializers.MultipleChoiceField(
        choices=media_tags, allow_empty=True, required=False
    )
    mandat = serializers.ChoiceField(
        choices=("municipal", "maire", "departemental", "regional", "consulaire"),
        required=False,
    )

    metadata = serializers.DictField(
        required=False, allow_empty=True, child=serializers.CharField(allow_blank=False)
    )

    next = serializers.CharField(required=False, allow_blank=True, write_only=True)

    referrer = serializers.CharField(required=False)

    PERSON_FIELDS = [
        "location_zip",
        "first_name",
        "last_name",
        "contact_phone",
        "date_of_birth",
        "gender",
        "media_preferences",
    ]

    def validate_email(self, value):
        if not subscription_mail_bucket.has_tokens(value):
            raise serializers.ValidationError(
                "Si vous n'avez pas encore reçu votre email de validation, attendez quelques instants."
            )
        return value

    def validate_contact_phone(self, value):
        return value and str(value)

    def validate_next(self, value):
        if not value or is_absolute_url(value):
            return ""
        return value

    def validate_location_zip(self, value):
        # Remove extra words and trucate
        # as people tend to add their city name to the location zip field
        max_length = person_fields["location_zip"].max_length
        value = value.split(" ")[0][:max_length]
        return value

    def validate_media_preferences(self, value):
        if isinstance(value, set):
            return ",".join(value)

        return value

    def validate(self, data):
        if (
            not data.get("location_country")
            or data.get("location_country") in FRANCE_COUNTRY_CODES
        ):
            data["location_country"] = french_zipcode_to_country_code(
                data["location_zip"]
            )

        return data

    def save(self):
        """Saves the subscription information.

        If there's already a person with that email address in the database, just update that row.

        If not, create and send a message with a confirmation link to that email address.
        """
        email = self.validated_data["email"]
        type = self.validated_data["type"]

        send_confirmation_email.delay(**self.validated_data)

        try:
            person = Person.objects.get_by_natural_key(email)
        except Person.DoesNotExist:
            self.result_data = {
                "status": "new",
                "url": SUBSCRIPTION_EMAIL_SENT_REDIRECT[type],
            }
        else:
            save_subscription_information(person, type, self.validated_data)

            self.result_data = {
                "status": "known",
                "id": str(person.id),
                "url": subscription_success_redirect_url(
                    type, person.id, self.validated_data
                ),
            }
            return person


class NewslettersField(serializers.DictField):
    child = serializers.BooleanField()

    def to_internal_value(self, data):
        value = super().to_internal_value(data)

        allowed_keys = Person.Newsletter.values
        wrong_keys = set(value).difference(allowed_keys)
        errors = [f"{key} n'est pas un nom de newsletter" for key in wrong_keys]

        if errors:
            raise ValidationError(errors)

        return value


class ManageNewslettersRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    newsletters = NewslettersField(required=False, default={})

    def validate_id(self, value):
        try:
            self.person = Person.objects.get(pk=value)
        except Person.DoesNotExist:
            raise ValidationError("Cette ID ne correspond pas à une personne connue")

    def save(self):
        for newsletter, target_status in self.validated_data["newsletters"].items():
            if newsletter in self.person.newsletters and not target_status:
                self.person.newsletters.remove(newsletter)
            elif newsletter not in self.person.newsletters and target_status:
                self.person.newsletters.append(newsletter)
        self.person.save()


class RetrievePersonRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    email = serializers.EmailField(required=False)

    def validate(self, attrs):
        non_empty = sum(1 for k, v in attrs.items() if v)
        if non_empty != 1:
            raise ValidationError("Indiquez soit un email, soit un id")

        return attrs

    def retrieve(self):
        try:
            if "id" in self.validated_data:
                return Person.objects.get(id=self.validated_data["id"])
            return Person.objects.get_by_natural_key(self.validated_data["email"])
        except Person.DoesNotExist:
            raise Http404("Aucune personne trouvée")


class PersonNewsletterListField(serializers.ListField):
    child = serializers.ChoiceField(choices=Person.Newsletter.choices)


class PersonMandatField(serializers.Field):
    requires_context = True
    types = tuple(types_elus.keys())
    choices = dict([(mandat, mandat) for mandat in types_elus.keys()])
    default_error_messages = {
        "invalid": "Le type de mandat n'est pas valide",
    }

    def get_defaults(self, mandat_type):
        defaults = {"statut": StatutMandat.INSCRIPTION_VIA_PROFIL}
        if mandat_type == "maire":
            defaults["mandat"] = MandatMunicipal.MANDAT_MAIRE
        return defaults

    def get_value(self, dictionary):
        return dictionary

    def get_attribute(self, instance):
        return instance

    def to_representation(self, person):
        return [
            mandat
            for mandat in self.types
            if types_elus[mandat]
            .objects.filter(person=person, **self.get_defaults(mandat))
            .exists()
        ]

    def to_internal_value(self, data):
        if not data.get("mandat", None):
            return None

        mandat_type = data.pop("mandat")

        if not mandat_type in self.types:
            return self.fail("invalid", data=data)
        try:
            types_elus[mandat_type].objects.get_or_create(
                person=self.context["request"].user.person,
                defaults=self.get_defaults(mandat_type),
            )
        except types_elus[mandat_type].MultipleObjectsReturned:
            pass

        return data


class PersonSerializer(FlexibleFieldsMixin, serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    email = serializers.EmailField(read_only=True)
    firstName = serializers.CharField(
        label="Prénom",
        max_length=person_fields["first_name"].max_length,
        required=False,
        allow_blank=True,
        source="first_name",
    )
    lastName = serializers.CharField(
        label="Nom",
        max_length=person_fields["last_name"].max_length,
        required=False,
        allow_blank=True,
        source="last_name",
    )
    displayName = serializers.CharField(
        label="Nom public",
        help_text="Le nom que tout le monde pourra voir. Indiquez par exemple votre prénom ou un pseudonyme.",
        max_length=person_fields["display_name"].max_length,
        required=True,
        source="display_name",
    )
    image = serializers.ImageField(
        required=False, label="Image de profil", default=None, source="image.thumbnail"
    )
    contactPhone = PhoneField(
        source="contact_phone",
        required=False,
        allow_blank=True,
        label="Numéro de téléphone",
    )

    isPoliticalSupport = serializers.BooleanField(
        source="is_political_support", required=False
    )

    mandat = PersonMandatField(required=False)

    referrerId = serializers.CharField(source="referrer_id", required=False)

    newsletters = PersonNewsletterListField(required=False, allow_empty=True)

    gender = serializers.CharField(required=False)

    address1 = serializers.CharField(
        required=False, allow_blank=True, source="location_address1"
    )
    address2 = serializers.CharField(
        required=False, allow_blank=True, source="location_address2"
    )
    zip = serializers.CharField(required=False, allow_blank=True, source="location_zip")
    city = serializers.CharField(
        required=False, allow_blank=True, source="location_city"
    )
    country = CountryField(
        required=False, allow_blank=False, default="FR", source="location_country"
    )
    actionRadius = serializers.IntegerField(
        source="action_radius", required=False, min_value=1, max_value=500
    )
    hasLocation = serializers.BooleanField(source="has_location", read_only=True)
    created = serializers.CharField(read_only=True)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if any(field in validated_data for field in instance.GEOCODING_FIELDS):
            geocode_person.delay(instance.pk)
        return instance

    class Meta:
        model = models.Person
        fields = (
            "id",
            "email",
            "firstName",
            "lastName",
            "displayName",
            "image",
            "contactPhone",
            "isPoliticalSupport",
            "referrerId",
            "newsletters",
            "gender",
            "address1",
            "address2",
            "zip",
            "city",
            "country",
            "mandat",
            "actionRadius",
            "hasLocation",
            "created",
        )


class ContactSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    subscriber = CurrentPersonField()
    firstName = serializers.CharField(
        label="Prénom",
        max_length=person_fields["first_name"].max_length,
        required=True,
        source="first_name",
    )
    lastName = serializers.CharField(
        label="Nom",
        max_length=person_fields["last_name"].max_length,
        required=True,
        source="last_name",
    )
    zip = serializers.CharField(
        required=True, source="location_zip", label="Code postal"
    )
    birthDate = serializers.DateField(
        source="date_of_birth",
        label="Date de naissance",
        required=False,
        allow_null=True,
    )
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = PhoneField(
        source="contact_phone",
        required=False,
        allow_blank=True,
        label="Numéro de téléphone",
    )
    subscribed = serializers.BooleanField(default=False)
    isLiaison = serializers.BooleanField(source="is_liaison", default=False)
    address = serializers.CharField(
        required=False,
        allow_blank=False,
        source="location_address1",
        label="Numéro et nom de la rue",
    )
    city = serializers.CharField(
        required=False,
        allow_blank=False,
        source="location_city",
        label="Nom de la ville",
    )
    country = CountryField(required=False, allow_blank=False, source="location_country")
    group = serializers.PrimaryKeyRelatedField(
        queryset=SupportGroup.objects.active(), required=False, allow_null=True
    )
    hasGroupNotifications = serializers.BooleanField(write_only=True, default=False)
    mediaPreferences = serializers.SlugRelatedField(
        source="tags",
        slug_field="label",
        many=True,
        queryset=PersonTag.objects.filter(label__in=(tag for tag, _desc in media_tags)),
        allow_empty=True,
        error_messages={
            "does_not_exist": _("« {value} » n'est pas un choix autorisé."),
        },
    )

    def validate_birthDate(self, value):
        if isinstance(value, date) and timezone.now().date() <= value:
            raise ValidationError("Veuillez indiquer une date dans le passé")

        return value

    def validate(self, data):
        if not data.get("email") and not data.get("contact_phone"):
            raise ValidationError(
                detail={
                    "global": "Veuillez indiquer obligatoirement une adresse email ou un numéro de téléphone mobile"
                }
            )

        if (
            not data.get("location_country")
            or data.get("location_country") in FRANCE_COUNTRY_CODES
        ):
            data["location_country"] = french_zipcode_to_country_code(
                data["location_zip"]
            )

        return data

    def create(self, validated_data):
        return save_contact_information(validated_data)

    class Meta:
        model = models.Person
        fields = (
            "id",
            "subscribed",
            "isLiaison",
            "firstName",
            "lastName",
            "zip",
            "birthDate",
            "gender",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "group",
            "hasGroupNotifications",
            "subscriber",
            "meta",
            "mediaPreferences",
        )
