from django.conf import settings
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from phonenumber_field.serializerfields import PhoneNumberField

from agir.lib.data import french_zipcode_to_country_code
from .models import Person
from .tasks import send_confirmation_email

from agir.lib.serializers import (
    LegacyBaseAPISerializer,
    LegacyLocationMixin,
    RelatedLabelField,
)


from . import models
from .actions.subscription import (
    SUBSCRIPTION_TYPE_LFI,
    SUBSCRIPTION_TYPE_CHOICES,
    SUBSCRIPTION_FIELD,
    nsp_confirmed_url,
)

person_fields = {f.name: f for f in models.Person._meta.get_fields()}


class PersonEmailSerializer(serializers.ModelSerializer):
    """Basic PersonEmail serializer used to show and edit PersonEmail
    """

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


class LegacyPersonSerializer(LegacyLocationMixin, LegacyBaseAPISerializer):
    tags = RelatedLabelField(
        many=True, required=False, queryset=models.PersonTag.objects.all()
    )

    email_opt_in = serializers.BooleanField(source="subscribed", required=False)

    email = serializers.EmailField(required=True)

    bounced = serializers.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not isinstance(self, LegacyUnprivilegedPersonSerializer):
            self.fields["emails"] = PersonEmailSerializer(
                required=False, many=True, context=self.context
            )

    def validate_email(self, value):

        try:
            pe = models.PersonEmail.objects.get_by_natural_key(value)
        except models.PersonEmail.DoesNotExist:
            return value

        if pe.person == self.instance:
            return pe.address

        raise serializers.ValidationError("Email already exists", code="unique")

    def update(self, instance, validated_data):
        emails = validated_data.pop("emails", None)
        email = validated_data.pop("email", None)
        with transaction.atomic():
            super().update(instance, validated_data)
            if emails is not None:
                for item in emails:
                    instance.add_email(
                        item["address"],
                        bounced=item.get("bounced", None),
                        bounced_date=item.get("bounced_date", None),
                    )

            if email is not None:
                if emails is None or email not in [item["address"] for item in emails]:
                    instance.add_email(email)
                instance.set_primary_email(email)

        return instance

    class Meta:
        model = models.Person
        fields = (
            "url",
            "_id",
            "id",
            "email",
            "emails",
            "first_name",
            "last_name",
            "bounced",
            "bounced_date",
            "_created",
            "_updated",
            "email_opt_in",
            "tags",
            "location",
        )
        read_only_fields = ("url", "_id", "_created", "_updated")
        extra_kwargs = {"url": {"view_name": "legacy:person-detail"}}


class LegacyUnprivilegedPersonSerializer(LegacyPersonSerializer):
    class Meta:
        model = models.Person
        fields = (
            "url",
            "_id",
            "email",
            "first_name",
            "last_name",
            "email_opt_in",
            "location",
        )
        read_only_fields = ("url", "_id")
        extra_kwargs = {"url": {"view_name": "legacy:person-detail"}}


class PersonTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonTag
        fields = ("url", "id", "label", "description")


class SubscriptionRequestSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=SUBSCRIPTION_TYPE_CHOICES, default=SUBSCRIPTION_TYPE_LFI, required=False
    )

    email = serializers.EmailField(required=True,)
    location_zip = serializers.RegexField(regex=r"^[0-9]{5}$", required=True)
    first_name = serializers.CharField(
        max_length=person_fields["first_name"].max_length, required=False
    )
    last_name = serializers.CharField(
        max_length=person_fields["last_name"].max_length, required=False
    )
    contact_phone = PhoneNumberField(required=False)

    PERSON_FIELDS = ["location_zip", "first_name", "last_name", "contact_phone"]

    def validate_contact_phone(self, value):
        print(value and str(value))
        return value and str(value)

    def save(self):
        """Sends the confirmation email to the subscribed person.

        Use only after having validated the serializer
        """
        email = self.validated_data["email"]
        type = self.validated_data["type"]

        try:
            person = Person.objects.get_by_natural_key(email)

            for f in self.PERSON_FIELDS:
                setattr(
                    person, f, self.validated_data.get(f, "") or getattr(person, f, "")
                )

            setattr(person, SUBSCRIPTION_FIELD[type], True)

            person.save()
            self.result_data = {
                "status": "known",
                "id": str(person.id),
                "url": nsp_confirmed_url(person),
            }
            return person

        except Person.DoesNotExist:
            location_country = french_zipcode_to_country_code(
                self.validated_data["location_zip"]
            )

            send_confirmation_email.delay(
                location_country=location_country, **self.validated_data
            )

            self.result_data = {
                "status": "new",
                "url": f"{settings.NSP_DOMAIN}/validez-votre-e-mail/",
            }


class NewslettersField(serializers.DictField):
    child = serializers.BooleanField()

    def to_internal_value(self, data):
        value = super().to_internal_value(data)

        allowed_keys = {key for key, label in Person.NEWSLETTERS_CHOICES}
        wrong_keys = set(value).difference(allowed_keys)
        errors = [f"{key} n'est pas un nom de newsletter" for key in wrong_keys]

        if errors:
            raise ValidationError(errors)

        return value


class ManageNewslettersRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    newsletters = NewslettersField()

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
