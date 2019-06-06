import secrets

import phonenumbers
import warnings

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models, transaction, IntegrityError
from django.db.models import Q
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django_prometheus.models import ExportModelOperationsMixin
from django.utils import timezone
from functools import partial
from nuntius.models import AbstractSubscriber

from phonenumber_field.modelfields import PhoneNumberField

from agir.lib.models import (
    BaseAPIResource,
    LocationMixin,
    AbstractLabel,
    NationBuilderResource,
    TimeStampedModel,
)
from agir.authentication.models import Role
from agir.lib.search import PrefixSearchQuery
from agir.lib.utils import generate_token_params
from . import metrics

from .model_fields import MandatesField, ValidatedPhoneNumberField

from .person_forms.models import *


class PersonQueryset(models.QuerySet):
    def with_contact_phone(self):
        return self.exclude(contact_phone="")

    def verified(self):
        return self.filter(contact_phone_status=Person.CONTACT_PHONE_VERIFIED)

    def full_text_search(self, query):
        q = Q(search=PrefixSearchQuery(query, config="simple_unaccented"))
        try:
            phonenumbers.parse(query, "FR")
        except phonenumbers.phonenumberutil.NumberParseException:
            return self.filter(q)
        else:
            return self.filter(q | Q(contact_phone__icontains=query[1:]))


class PersonManager(models.Manager.from_queryset(PersonQueryset)):
    def get(self, *args, **kwargs):
        if "email" in kwargs:
            kwargs["emails__address"] = kwargs["email"]
            del kwargs["email"]
        return super().get(*args, **kwargs)

    def create(self, *args, **kwargs):
        warnings.warn(
            "You shoud use create_person or create_superperson.", DeprecationWarning
        )
        if "email" not in kwargs:
            raise ValueError("Email must be set")
        email = kwargs.pop("email")
        kwargs.setdefault("is_staff", False)
        kwargs.setdefault("is_superuser", False)
        person = self._create_person(email, kwargs.get("password", None), **kwargs)

        return person

    def get_by_natural_key(self, email):
        email_field_class = self.model.emails.rel.related_model
        try:
            return email_field_class.objects.get_by_natural_key(email).person
        except email_field_class.DoesNotExist:
            raise self.model.DoesNotExist

    def _create_person(
        self, email, password, *, is_staff, is_superuser, is_active=True, **extra_fields
    ):
        """
        Creates and saves a person with the given username, email and password.
        """
        if not email:
            raise ValueError("The given email must be set")

        role = Role(
            type=Role.PERSON_ROLE,
            is_staff=is_staff,
            is_superuser=is_superuser,
            is_active=is_active,
        )
        role.set_password(password)

        with transaction.atomic():
            role.save()

            person = self.model(role=role, **extra_fields)
            person.save(using=self._db)

            person.add_email(email)

        if not settings.MAILTRAIN_DISABLE:
            from .tasks import update_person_mailtrain

            transaction.on_commit(partial(update_person_mailtrain.delay, person.pk))

        return person

    def create_person(self, email, password=None, **extra_fields):
        """
        Create a user
        :param email: the user's email
        :param password: optional password that may be used to connect to the admin website
        :param extra_fields: any other field
        :return:
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        if not extra_fields.get("is_insoumise", True):
            extra_fields.setdefault("subscribed", False)
            extra_fields.setdefault("event_notifications", False)
            extra_fields.setdefault("group_notifications", False)

        return self._create_person(email, password, **extra_fields)

    def create_superperson(self, email, password, **extra_fields):
        """
        Create a superuser
        :param email:
        :param password:
        :param extra_fields:
        :return:
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_person(email, password, **extra_fields)

    def set_subscriber_status(self, email, status):
        try:
            p = self.get(email=email)
        except Person.DoesNotExist:
            pass
        else:
            if status == AbstractSubscriber.STATUS_BOUNCED:
                p.bounced = True
                p.save()
            elif status == AbstractSubscriber.STATUS_COMPLAINED:
                p.subscribed = False
                p.save()


class Person(
    AbstractSubscriber,
    ExportModelOperationsMixin("person"),
    BaseAPIResource,
    NationBuilderResource,
    LocationMixin,
):
    """
    Model that represents a physical person that signed as a JLM2017 supporter

    A person is identified by the email address he's signed up with.
    He is associated with permissions that determine what he can and cannot do
    with the API.

    He has an optional password, which will be only used to authenticate him with
    the API admin.
    """

    objects = PersonManager()

    role = models.OneToOneField(
        "authentication.Role", on_delete=models.PROTECT, related_name="person"
    )
    auto_login_salt = models.CharField(max_length=255, blank=True, default="")

    is_insoumise = models.BooleanField(_("Insoumis⋅e"), default=True)

    subscribed = models.BooleanField(
        _("Recevoir les lettres d'information"),
        default=True,
        blank=True,
        help_text=_(
            "Vous recevrez les lettres de la France insoumise, notamment : les lettres d'information, les"
            " appels à volontaires, les annonces d'émissions ou d'événements..."
        ),
    )

    subscribed_sms = models.BooleanField(
        _("Recevoir les SMS d'information"),
        default=True,
        blank=True,
        help_text=_(
            "Vous recevrez des SMS de la France insoumise comme des meeting près de chez vous ou des appels à volontaire..."
        ),
    )

    event_notifications = models.BooleanField(
        _("Recevoir les notifications des événements"),
        default=True,
        blank=True,
        help_text=_(
            "Vous recevrez des messages quand les informations des évènements auxquels vous souhaitez participer"
            " sont mis à jour ou annulés."
        ),
    )

    group_notifications = models.BooleanField(
        _("Recevoir les notifications de mes groupes"),
        default=True,
        blank=True,
        help_text=_(
            "Vous recevrez des messages quand les informations du groupe change, ou quand le groupe organise des"
            " événements."
        ),
    )

    draw_participation = models.BooleanField(
        _("Participer aux tirages au sort"),
        default=False,
        blank=True,
        help_text=_(
            "Vous pourrez être tiré⋅e au sort parmis les Insoumis⋅es pour participer à des événements comme la Convention."
            "Vous aurez la possibilité d'accepter ou de refuser cette participation."
        ),
    )

    first_name = models.CharField(_("prénom"), max_length=255, blank=True)
    last_name = models.CharField(_("nom de famille"), max_length=255, blank=True)

    tags = models.ManyToManyField("PersonTag", related_name="people", blank=True)

    CONTACT_PHONE_UNVERIFIED = "U"
    CONTACT_PHONE_VERIFIED = "V"
    CONTACT_PHONE_PENDING = "P"
    CONTACT_PHONE_STATUS_CHOICES = (
        (CONTACT_PHONE_UNVERIFIED, _("Non vérifié")),
        (CONTACT_PHONE_VERIFIED, _("Vérifié")),
        (CONTACT_PHONE_PENDING, _("En attente de validation manuelle")),
    )

    contact_phone = ValidatedPhoneNumberField(
        _("Numéro de téléphone de contact"),
        blank=True,
        validated_field_name="contact_phone_status",
        unverified_value=CONTACT_PHONE_UNVERIFIED,
    )
    contact_phone_status = models.CharField(
        _("Statut du numéro de téléphone"),
        choices=CONTACT_PHONE_STATUS_CHOICES,
        max_length=1,
        default=CONTACT_PHONE_UNVERIFIED,
        help_text=_(
            "Pour les numéros hors France métropolitaine, merci de les indiquer sous la forme internationale,"
            " en les préfixant par '+' et le code du pays."
        ),
    )

    GENDER_FEMALE = "F"
    GENDER_MALE = "M"
    GENDER_OTHER = "O"
    GENDER_CHOICES = (
        (GENDER_FEMALE, _("Femme")),
        (GENDER_MALE, _("Homme")),
        (GENDER_OTHER, _("Autre/Non défini")),
    )
    gender = models.CharField(
        _("Genre"), max_length=1, blank=True, choices=GENDER_CHOICES
    )
    date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)

    mandates = MandatesField(_("Mandats électoraux"), default=list, blank=True)

    meta = JSONField(_("Autres données"), default=dict, blank=True)

    search = SearchVectorField("Données de recherche", editable=False, null=True)

    class Meta:
        verbose_name = _("personne")
        verbose_name_plural = _("personnes")
        ordering = ("-created",)
        # add permission 'view'
        default_permissions = ("add", "change", "delete", "view")
        indexes = (
            GinIndex(fields=["search"], name="search_index"),
            models.Index(fields=["contact_phone"], name="contact_phone_index"),
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            metrics.subscriptions.inc()

        return super().save(*args, **kwargs)

    def __str__(self):
        if self.first_name and self.last_name:
            return "{} {} <{}>".format(self.first_name, self.last_name, self.email)
        else:
            return self.email or "<pas d'email>"

    def __repr__(self):
        return f"{self.__class__.__name__}(pk={self.pk!r}, email={self.email})"

    @property
    def email(self):
        return self.primary_email.address if self.primary_email else ""

    @cached_property
    def primary_email(self):
        try:
            return self.emails.first()
        except PersonEmail.DoesNotExist:
            return None

    @property
    def bounced(self):
        return self.primary_email.bounced

    @bounced.setter
    def bounced(self, value):
        self.primary_email.bounced = value
        self.primary_email.save()

    @property
    def bounced_date(self):
        return self.primary_email.bounced_date

    @bounced_date.setter
    def bounced_date(self, value):
        self.primary_email.bounced_date = value
        self.primary_email.save()

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name or self.email

    def add_email(self, email_address, primary=False, **kwargs):
        try:
            email = self.emails.get_by_natural_key(email_address)
        except PersonEmail.DoesNotExist:
            email = PersonEmail.objects.create_email(
                address=email_address, person=self, **kwargs
            )
        else:
            email.bounced = kwargs.get("bounced", email.bounced) or False
            email.bounced_date = kwargs.get("bounced_date", email.bounced_date)
            email.save()

        if primary and email.person == self:
            self.set_primary_email(email)

    def set_primary_email(self, email_address):
        if isinstance(email_address, PersonEmail):
            email_instance = email_address
        else:
            email_instance = self.emails.get_by_natural_key(email_address)
        order = list(self.get_personemail_order())
        order.remove(email_instance.id)
        order.insert(0, email_instance.id)
        self.set_personemail_order(order)
        self.primary_email = email_instance

    def get_subscriber_status(self):
        if self.bounced:
            return AbstractSubscriber.STATUS_BOUNCED
        if not self.subscribed:
            return AbstractSubscriber.STATUS_UNSUBSCRIBED
        return AbstractSubscriber.STATUS_SUBSCRIBED

    def get_subscriber_email(self):
        return self.email

    def get_subscriber_data(self):
        data = super().get_subscriber_data()

        return {**data, "login_query": urlencode(generate_token_params(self))}


class PersonTag(AbstractLabel):
    """
    Model that represents a tag that may be used to qualify people
    """

    exported = models.BooleanField(_("Exporté vers mailtrain"), default=False)

    class Meta:
        verbose_name = _("tag")


class PersonEmailManager(models.Manager):
    @classmethod
    def normalize_email(cls, email, *, lowercase_local_part=False):
        try:
            local_part, domain = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = "@".join(
                [
                    local_part.lower() if lowercase_local_part else local_part,
                    domain.lower(),
                ]
            )
        return email

    def create_email(self, address, person, *, lowercase_local_part=False, **kwargs):
        return self.create(
            address=self.normalize_email(
                address, lowercase_local_part=lowercase_local_part
            ),
            person=person,
            **kwargs,
        )

    def get_by_natural_key(self, address):
        # look first without lowercasing email
        return self.get(address__iexact=address)


class PersonEmail(ExportModelOperationsMixin("person_email"), models.Model):
    """
    Model that represent a person email address
    """

    objects = PersonEmailManager()

    address = models.EmailField(
        _("adresse email"),
        blank=False,
        help_text=_("L'adresse email de la personne, utilisée comme identifiant"),
    )

    _bounced = models.BooleanField(
        _("email rejeté"),
        default=False,
        db_column="bounced",
        help_text=_(
            "Indique que des mails envoyés ont été rejetés par le serveur distant"
        ),
    )

    bounced_date = models.DateTimeField(
        _("date de rejet de l'email"),
        null=True,
        blank=True,
        help_text=_("Si des mails ont été rejetés, indique la date du dernier rejet"),
    )

    @property
    def bounced(self):
        return self._bounced

    @bounced.setter
    def bounced(self, value):
        if value and self._bounced is False:
            self.bounced_date = timezone.now()
        self._bounced = value

    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, null=False, related_name="emails"
    )

    class Meta:
        order_with_respect_to = "person"
        verbose_name = _("Email")

    def __str__(self):
        return self.address

    def validate_unique(self, exclude=None):
        errors = {}
        try:
            super().validate_unique(exclude=exclude)
        except ValidationError as e:
            errors = e.message_dict

        if exclude is None or "address" not in exclude:
            qs = PersonEmail.objects.filter(address__iexact=self.address)
            if not self._state.adding and self.pk:
                qs = qs.exclude(pk=self.pk)

            if qs.exists():
                errors.setdefault("address", []).append(
                    ValidationError(
                        message=_("Cette adresse email est déjà utilisée."),
                        code="unique",
                    )
                )

        if errors:
            raise ValidationError(errors)

    def clean(self):
        self.address = PersonEmail.objects.normalize_email(self.address)


def generate_code():
    return str(secrets.randbelow(1_000_000)).zfill(6)


class PersonValidationSMS(
    ExportModelOperationsMixin("person_validation_sms"), TimeStampedModel
):
    person = models.ForeignKey("Person", on_delete=models.CASCADE, editable=False)
    phone_number = PhoneNumberField(_("Numéro de mobile"), editable=False)
    code = models.CharField(max_length=8, editable=False, default=generate_code)

    class Meta:
        verbose_name = _("SMS de validation")
        verbose_name_plural = _("SMS de validation")
