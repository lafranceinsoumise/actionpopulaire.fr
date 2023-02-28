import secrets
import warnings
from datetime import datetime
from functools import reduce
from operator import or_

import phonenumbers
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models, transaction, IntegrityError
from django.db.models import JSONField, Subquery, OuterRef, DateTimeField, Prefetch
from django.db.models import Q
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone, formats
from django.utils.functional import cached_property
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from dynamic_filenames import FilePattern
from nuntius.models import AbstractSubscriber
from phonenumber_field.modelfields import PhoneNumberField
from push_notifications.models import APNSDevice, GCMDevice
from stdimage.models import StdImageField

from agir.authentication.models import Role
from agir.lib.models import (
    BaseAPIResource,
    LocationMixin,
    AbstractLabel,
    TimeStampedModel,
)
from agir.lib.search import PrefixSearchQuery
from agir.lib.utils import generate_token_params, resize_and_autorotate
from . import metrics
from .model_fields import MandatesField, ValidatedPhoneNumberField
from .person_forms.models import *
from ..elus.models import StatutMandat
from ..events.models import CustomDateTimeField
from ..lib.display import genrer
from ..lib.form_fields import CustomJSONEncoder
from ..lib.model_fields import ChoiceArrayField

__all__ = [
    "Person",
    "PersonEmail",
    "PersonTag",
    "Qualification",
    "PersonQualification",
    "PersonForm",
    "PersonFormSubmission",
    "PersonValidationSMS",
]


person_image_path = FilePattern(
    filename_pattern="{app_label}/{model_name}/{instance.id}/{uuid:s}{ext}"
)


class PersonQueryset(models.QuerySet):
    def with_active_role(self):
        return self.filter(role__is_active=True)

    def with_contact_phone(self):
        return self.exclude(contact_phone="")

    def with_prefetched_email(self):
        return self.annotate(
            prefetched_email=PersonEmail.objects.filter(person_id=OuterRef("id"))
            .order_by("_bounced", "_order")
            .values("address")[:1],
        )

    def as_email_recipients(self):
        return (
            self.with_active_role()
            .with_prefetched_email()
            .values_list("prefetched_email", flat=True)
        )

    def verified(self):
        return self.filter(contact_phone_status=Person.CONTACT_PHONE_VERIFIED)

    def search(self, query, *or_query):
        q = reduce(
            lambda a, b: a | Q(search=PrefixSearchQuery(b, config="simple_unaccented")),
            or_query,
            Q(search=PrefixSearchQuery(query, config="simple_unaccented")),
        )
        try:
            phonenumbers.parse(query, "FR")
        except phonenumbers.phonenumberutil.NumberParseException:
            return self.filter(q)
        else:
            return self.filter(q | Q(contact_phone__icontains=query[1:]))

    def annotate_elus(self, current=True):
        from agir.elus.models import types_elus

        annotations = {
            f"elu_{label}": klass.objects.filter(
                person_id=models.OuterRef("id")
            ).exclude(statut=StatutMandat.FAUX)
            for label, klass in types_elus.items()
        }

        if current:
            today = timezone.now().date()
            annotations = {
                label: subq.filter(dates__contains=today)
                for label, subq in annotations.items()
            }

        return self.annotate(
            **{label: models.Exists(subq) for label, subq in annotations.items()}
        )

    def elus(self, current=True):
        from agir.elus.models import types_elus

        return self.annotate_elus(current).filter(
            reduce(or_, (Q(**{f"elu_{label}": True}) for label in types_elus))
        )

    def app(self, installed=True):
        if installed:
            return self.exclude(Q(role__apnsdevice=None) & Q(role__gcmdevice=None))
        return self.filter(Q(role__apnsdevice=None) & Q(role__gcmdevice=None))

    def liaisons(self, from_date=None, to_date=None):
        from agir.people.actions.subscription import DATE_2022_LIAISON_META_PROPERTY

        liaison_form_submissions = (
            PersonFormSubmission.objects.filter(
                person=OuterRef("pk"), form__slug="correspondant-es-2022"
            )
            .order_by("created")
            .values("created")
        )
        liaisons = self.filter(
            newsletters__contains=[Person.NEWSLETTER_2022_LIAISON]
        ).annotate(
            liaison_date=Coalesce(
                Subquery(liaison_form_submissions[:1]),
                Cast(
                    KeyTextTransform(DATE_2022_LIAISON_META_PROPERTY, "meta"),
                    DateTimeField(),
                ),
                "created",
            )
        )
        if from_date:
            liaisons = liaisons.filter(liaison_date__date__gte=from_date)
        if to_date:
            liaisons = liaisons.filter(liaison_date__date__lte=to_date)

        return liaisons.order_by("liaison_date")


def get_default_display_name(
    email="", first_name="", last_name="", display_name="", **kwargs
):
    if display_name:
        return display_name

    if first_name and last_name:
        base = "{}{}".format(first_name[:1], last_name[:1])
    elif first_name:
        base = first_name[:2]
    elif last_name:
        base = last_name[:2]
    elif email:
        base = email[:2]
    else:
        return "?"

    return base.upper()


class PersonManager(models.Manager.from_queryset(PersonQueryset)):
    def get(self, *args, **kwargs):
        if "email" in kwargs:
            kwargs["emails__address"] = kwargs["email"]
            del kwargs["email"]
        return super().get(*args, **kwargs)

    def create(self, *args, **kwargs):
        warnings.warn(
            "You shoud use create_person.",
            DeprecationWarning,
        )
        return self.create_person(*args, **kwargs)

    def get_by_natural_key(self, email):
        email_field_class = self.model.emails.rel.related_model
        try:
            return email_field_class.objects.get_by_natural_key(email).person
        except email_field_class.DoesNotExist:
            raise self.model.DoesNotExist

    def _create_person(
        self,
        email,
        password,
        *,
        is_staff,
        is_superuser,
        is_active=True,
        create_role=False,
        **extra_fields,
    ):
        """
        Creates and saves a person with the given username, email and password.
        """
        if password or is_staff or is_superuser or not is_active:
            create_role = True

        with transaction.atomic():
            if create_role:
                role = Role(
                    type=Role.PERSON_ROLE,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                    is_active=is_active,
                )
                if password:
                    role.set_password(password)

                role.save()
            else:
                role = None

            if (
                not hasattr(extra_fields, "display_name")
                or not extra_fields["display_name"]
            ):
                extra_fields["display_name"] = get_default_display_name(
                    email=email, **extra_fields
                )

            person = self.model(role=role, **extra_fields)
            person.save(using=self._db)

            if email:
                person.add_email(email, primary=True)

        return person

    def create_person(self, email, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("password", None)
        return self._create_person(email, **extra_fields)

    def create_2022(self, email, password=None, *, subscribed=None, **extra_fields):
        """
        Create a user
        :param email: the user's email
        :param password: optional password that may be used to connect to the admin website
        :param extra_fields: any other field
        :return:
        """
        extra_fields.setdefault("is_2022", True)

        if subscribed is False:
            extra_fields.setdefault("newsletters", [])
        else:
            extra_fields.setdefault(
                "newsletters",
                [Person.NEWSLETTER_2022, Person.NEWSLETTER_2022_EXCEPTIONNEL],
            )

        return self.create_person(email, password=password, **extra_fields)

    def create_insoumise(
        self, email, password=None, *, subscribed=None, **extra_fields
    ):
        """
        Create a user
        :param email: the user's email
        :param password: optional password that may be used to connect to the admin website
        :param extra_fields: any other field
        :return:
        """
        extra_fields.setdefault("is_insoumise", True)

        if subscribed is False:
            extra_fields.setdefault("newsletters", [])
        else:
            extra_fields.setdefault(
                "newsletters",
                [Person.NEWSLETTER_LFI],
            )

        return self.create_person(email, password=password, **extra_fields)

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

    def get_subscriber(self, email):
        try:
            return self.get(email=email)
        except Person.DoesNotExist:
            pass

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
                p.newsletters = []
                p.save()


def generate_referrer_id():
    return secrets.token_urlsafe(9)


class Person(
    AbstractSubscriber,
    ExportModelOperationsMixin("person"),
    BaseAPIResource,
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
        "authentication.Role",
        on_delete=models.PROTECT,
        related_name="person",
        null=True,
    )
    auto_login_salt = models.CharField(max_length=255, blank=True, default="")

    is_insoumise = models.BooleanField(_("Insoumis⋅e"), default=False)
    is_2022 = models.BooleanField(_("Soutien 2022"), default=False)

    MEMBRE_RESEAU_INCONNU = "I"
    MEMBRE_RESEAU_SOUHAITE = "S"
    MEMBRE_RESEAU_OUI = "O"
    MEMBRE_RESEAU_NON = "N"
    MEMBRE_RESEAU_EXCLUS = "E"
    MEMBRE_RESEAU_CHOICES = (
        (MEMBRE_RESEAU_INCONNU, "Inconnu / Non pertinent"),
        (MEMBRE_RESEAU_SOUHAITE, "Souhaite faire partie du réseau des élus"),
        (MEMBRE_RESEAU_OUI, "Fait partie du réseau des élus"),
        (MEMBRE_RESEAU_NON, "Ne souhaite pas faire partie du réseau des élus"),
        (MEMBRE_RESEAU_EXCLUS, "Exclus du réseau"),
    )
    membre_reseau_elus = models.CharField(
        _("Membre du réseau des élus"),
        max_length=1,
        blank=False,
        null=False,
        choices=MEMBRE_RESEAU_CHOICES,
        default=MEMBRE_RESEAU_INCONNU,
        help_text="Pertinent uniquement si la personne a un ou plusieurs mandats électoraux.",
    )

    NEWSLETTER_LFI = "LFI"
    NEWSLETTER_LJI = "LJI"
    NEWSLETTER_2022 = "2022"
    NEWSLETTER_2022_EXCEPTIONNEL = "2022_exceptionnel"
    NEWSLETTER_2022_EN_LIGNE = "2022_en_ligne"
    NEWSLETTER_2022_CHEZ_MOI = "2022_chez_moi"
    NEWSLETTER_2022_PROGRAMME = "2022_programme"
    NEWSLETTER_2022_LIAISON = "2022_liaison"
    NEWSLETTERS_CHOICES = (
        (NEWSLETTER_LFI, "Lettre d'information de la France insoumise"),
        (NEWSLETTER_LJI, "Informations jeunes insoumis"),
        (NEWSLETTER_2022, "Lettre d'information NSP"),
        (NEWSLETTER_2022_EXCEPTIONNEL, "NSP : informations exceptionnelles"),
        (NEWSLETTER_2022_EN_LIGNE, "NSP actions en ligne"),
        (NEWSLETTER_2022_CHEZ_MOI, "NSP agir près de chez moi"),
        (NEWSLETTER_2022_PROGRAMME, "NSP processus programme"),
        (NEWSLETTER_2022_LIAISON, "NSP Correspondant·e d'immeuble ou de rue"),
    )

    newsletters = ChoiceArrayField(
        models.CharField(choices=NEWSLETTERS_CHOICES, max_length=255),
        default=list,
        blank=True,
    )

    subscribed_sms = models.BooleanField(
        _("Recevoir les SMS d'information"),
        default=True,
        blank=True,
        help_text=_(
            "Nous envoyons parfois des SMS plutôt que des emails lors des grands événements&nbsp;! Vous ne recevrez que "
            "les informations auxquelles vous êtes abonné⋅e."
        ),
    )

    event_notifications = models.BooleanField(
        _("Recevoir les notifications des événements"),
        default=True,
        blank=True,
        help_text=_(
            "Vous recevrez des messages quand les informations des événements auxquels vous souhaitez participer"
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

    display_name = models.CharField(_("nom d'affichage"), max_length=255)

    image = StdImageField(
        _("image de profil"),
        upload_to=person_image_path,
        render_variations=resize_and_autorotate,
        variations={"thumbnail": (200, 200, True), "admin_thumbnail": (100, 100, True)},
        blank=True,
        help_text=_("Vous pouvez ajouter une image publique de profil"),
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "gif", "png"])
        ],
    )

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

    meta = JSONField(
        _("Autres données"), default=dict, blank=True, encoder=CustomJSONEncoder
    )

    commentaires = models.TextField(
        "Commentaires",
        blank=True,
        help_text="ATTENTION : en cas de demande d'accès à ses données par la personne concernée par cette fiche, le"
        " contenu de ce champ lui sera communiqué. N'indiquez ici que des éléments factuels.",
    )

    crp = models.TextField(
        "Notes CRP",
        blank=True,
        null=False,
        default="",
        help_text="Champ reservé aux notes du Comité de Respect des Principes concernant cette personne",
    )

    search = SearchVectorField("Données de recherche", editable=False, null=True)

    referrer_id = models.CharField(
        "Identifiant d'invitation",
        default=generate_referrer_id,
        max_length=13,
        unique=True,
    )

    # Read-only cache value for the primary_email.address value
    # This value will be automatically generated / updated through
    # a SQL trigger (cf. agir.people.migrations.0013_person__email
    _email = models.EmailField(
        _("adresse email"),
        editable=False,
        null=False,
        default="",
        help_text=_("L'adresse email principale de la personne"),
    )

    public_email = models.OneToOneField(
        "people.PersonEmail",
        on_delete=models.SET_NULL,
        verbose_name="Adresse email publique",
        related_name="person_with_public_email",
        related_query_name="person_with_public_email",
        null=True,
        blank=True,
        default=None,
        help_text=_(
            "L'adresse email à afficher publiquement dans l'application pour cette personne. "
            "Si vide, l'adresse email principale de la personne sera utilisée."
        ),
    )

    class Meta:
        verbose_name = _("personne")
        verbose_name_plural = _("personnes")
        ordering = ("-created",)
        # add permission 'view'
        default_permissions = ("add", "change", "delete", "view")
        permissions = [
            (
                "select_person",
                "Peut lister pour sélectionner (dans un Select 2 par exemple)",
            ),
            (
                "export_people",
                "Peut faire un export des informations des personnes",
            ),
            (
                "crp",
                "Peut voir et modifier les notes du Comité de Respect des Principes",
            ),
        ]
        indexes = (
            GinIndex(fields=["search"], name="search_index"),
            models.Index(fields=["contact_phone"], name="contact_phone_index"),
            models.Index(fields=["created"], name="created_index"),
            models.Index(fields=["created", "id"], name="created_id_index"),
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            metrics.subscriptions.inc()

        return super().save(*args, **kwargs)

    def __str__(self):
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        if self.display_name:
            parts.append(f"({self.display_name})")
        if self.display_email:
            parts.append(f"<{self.display_email}>")

        if parts:
            return " ".join(parts)
        else:
            return "<aucune nom ou email>"

    def __repr__(self):
        return f"{self.__class__.__name__}(pk={self.pk!r}, email={self.display_email})"

    @property
    def is_agir(self):
        return self.is_insoumise and self.created <= datetime(
            2020, 12, 6, tzinfo=timezone.get_default_timezone()
        )

    @property
    def email(self):
        if self._email:
            return self._email
        if self.primary_email:
            return self.primary_email.address
        return ""

    @property
    def is_2022_only(self):
        return self.is_2022 and not self.is_insoumise

    @property
    def is_insoumise_only(self):
        return self.is_insoumise and not self.is_2022

    @cached_property
    def primary_email(self):
        return self.emails.filter(_bounced=False).first() or self.emails.first()

    @property
    def display_email(self):
        if self.public_email:
            return self.public_email.address
        if self.primary_email:
            return self.primary_email.address
        return ""

    @display_email.setter
    def display_email(self, value):
        if not value:
            self.public_email = None
            self.save(update_fields="public_email")
        else:
            self.add_email(value, public=True)

    @property
    def bounced(self):
        if self.primary_email is None:
            return None
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

    @property
    def subscribed(self):
        return self.NEWSLETTER_LFI in self.newsletters

    @subscribed.setter
    def subscribed(self, value):
        if value and not self.subscribed:
            self.newsletters.append(self.NEWSLETTER_LFI)
        if not value and self.subscribed:
            self.newsletters.remove(self.NEWSLETTER_LFI)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip() or self.display_email

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name or self.display_email

    @property
    def formule_adresse(self):
        nom = self.first_name

        if nom:
            cher = genrer(self.gender, "Cher", "Chère", "Chèr⋅e")
            return f"{cher} {nom}"

        return "Bonjour"

    @property
    def formule_adresse_insoumise(self):
        cher = genrer(self.gender, "Cher", "Chère", "Chèr⋅e")

        if self.first_name and self.last_name:
            designation = self.get_full_name()
        else:
            designation = genrer(self.gender, "insoumis⋅e")

        return f"{cher} {designation}"

    def add_email(self, email_address, primary=False, public=False, **kwargs):
        try:
            if isinstance(email_address, PersonEmail):
                email = email_address
            else:
                email = self.emails.get_by_natural_key(email_address)
        except PersonEmail.DoesNotExist:
            email = PersonEmail.objects.create_email(
                address=email_address, person=self, **kwargs
            )
        else:
            if email.person != self:
                raise IntegrityError(
                    f"L'email '{email_address}' est déjà associé à une autre personne"
                )

            email.bounced = kwargs.get("bounced", email.bounced) or False
            email.bounced_date = kwargs.get("bounced_date", email.bounced_date)
            email.save()

        if primary:
            self.set_primary_email(email)
            self._email = email.address

        if public:
            self.public_email = email

        self.save(update_fields=("_email", "public_email"))

        return email

    def set_primary_email(self, email_address):
        if isinstance(email_address, PersonEmail):
            email_instance = email_address
        else:
            email_instance = self.emails.get_by_natural_key(email_address)
        order = list(self.get_personemail_order())
        order.remove(email_instance.id)
        order.insert(0, email_instance.id)
        self.set_personemail_order(order)
        self.__dict__["primary_email"] = email_instance

    def get_subscriber_status(self):
        if self.bounced:
            return AbstractSubscriber.STATUS_BOUNCED
        if self.email:
            domain = self.email.rsplit("@", maxsplit=1)[-1].upper()
            if domain not in settings.BLOCKED_EMAIL_DOMAINS:
                return AbstractSubscriber.STATUS_SUBSCRIBED
        return AbstractSubscriber.STATUS_UNSUBSCRIBED

    def get_subscriber_email(self):
        return self.email

    def get_subscriber_data(self):
        data = super().get_subscriber_data()

        return {
            **data,
            "login_query": mark_safe(urlencode(generate_token_params(self))),
            "greeting": self.formule_adresse,
            "full_name": self.get_full_name(),
            "short_name": self.get_short_name(),
            "ancienne_region": self.ancienne_region,
            "region": self.region,
            "departement": self.departement,
            "city": self.location_city,
            "short_address": self.short_address,
            "short_location": self.short_location(),
            "full_address": self.html_full_address(),
            "meta": self.meta,
        }

    def get_subscriber_push_devices(self):
        apns_devices = list(
            APNSDevice.objects.filter(user_id=self.role_id, active=True)
        )
        gcm_devices = list(GCMDevice.objects.filter(user_id=self.role_id, active=True))
        return apns_devices + gcm_devices

    def ensure_role_exists(self):
        """Crée un compte pour cette personne si aucun n'existe.

        Cette méthode n'a aucun effet si un compte existe déjà.
        """
        if self.role_id is not None:
            return

        with transaction.atomic():
            self.role = Role.objects.create(
                is_active=True,
                is_staff=False,
                is_superuser=False,
                type=Role.PERSON_ROLE,
            )
            self.save(update_fields=["role"])

    def has_perm(self, perm, obj=None):
        """Simple raccourci pour vérifier les permissions"""
        return self.role.has_perm(perm, obj)


class PersonTag(AbstractLabel):
    """
    Model that represents a tag that may be used to qualify people
    """

    exported = models.BooleanField(_("Exporté vers mailtrain"), default=False)

    class Meta:
        verbose_name = _("tag")


class Qualification(AbstractLabel):
    """
    Model that represents a tag that may be used to qualify people through a PersonQualification instance
    """

    class Meta:
        verbose_name = _("type de statut")
        verbose_name_plural = _("types de statuts")


class PersonQualificationQueryset(models.QuerySet):
    def effective(self):
        now = timezone.now()
        return self.filter(
            Q(start_time__isnull=True, end_time__isnull=True)
            | Q(start_time__isnull=True, end_time__gte=now)
            | Q(end_time__isnull=True, start_time__lte=now)
            | Q(start_time__lte=now, end_time__gte=now)
        )

    def past(self):
        now = timezone.now()
        return self.filter(end_time__isnull=False, end_time__lt=now)

    def future(self):
        now = timezone.now()
        return self.filter(start_time__isnull=False, start_time__gt=now)

    def only_statuses(self, statuses=None):
        if statuses is None:
            return self
        available_statuses = PersonQualification.Status.values
        clean_statuses = set(
            [status for status in statuses if status in available_statuses]
        )
        # Do not filter if no status is selected or all are
        if not clean_statuses or len(clean_statuses) == len(available_statuses):
            return self

        query = self.none()

        if PersonQualification.Status.EFFECTIVE in clean_statuses:
            query = query | self.effective()
        if PersonQualification.Status.PAST in clean_statuses:
            query = query | self.past()
        if PersonQualification.Status.FUTURE in clean_statuses:
            query = query | self.future()

        return query


class PersonQualification(TimeStampedModel):
    """
    Model that represents a tag that may be used to qualify people and that may be temporary
    if a value is specified for its start_time and/or end_time fields
    """

    class Status(models.TextChoices):
        EFFECTIVE = "E", "Statut effectif"
        PAST = "P", "Statut passé"
        FUTURE = "F", "Statut futur"

    objects = PersonQualificationQueryset.as_manager()

    person = models.ForeignKey(
        "people.Person",
        verbose_name=_("personne"),
        related_name="person_qualifications",
        related_query_name="person_qualification",
        on_delete=models.CASCADE,
    )
    qualification = models.ForeignKey(
        "people.Qualification",
        verbose_name=_("type de statut"),
        related_name="person_qualifications",
        related_query_name="person_qualification",
        on_delete=models.CASCADE,
    )
    description = models.TextField(_("description"), null=False, blank=True)
    start_time = CustomDateTimeField(_("date et heure de début"), null=True, blank=True)
    end_time = CustomDateTimeField(_("date et heure de fin"), null=True, blank=True)

    @property
    def status(self):
        now = timezone.now()
        if self.end_time and self.end_time < now:
            return self.Status.PAST
        if self.start_time and self.start_time > now:
            return self.Status.FUTURE
        return self.Status.EFFECTIVE

    @property
    def is_effective(self):
        return self.status == self.Status.EFFECTIVE

    def get_range_display(self):
        strings = []
        if self.start_time:
            strings.append(
                _("du {date}, {time}").format(
                    date=formats.date_format(self.start_time, "DATE_FORMAT"),
                    time=formats.date_format(self.start_time, "TIME_FORMAT"),
                )
            )
        if self.end_time:
            strings.append(
                _("jusqu'au {date}, {time}").format(
                    date=formats.date_format(self.end_time, "DATE_FORMAT"),
                    time=formats.date_format(self.end_time, "TIME_FORMAT"),
                )
            )

        return " ".join(strings)

    def clean(self):
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValidationError(
                {
                    "start_time": _(
                        "La date de début doit être antérieure à celle de fin"
                    ),
                    "end_time": _(
                        "La date de fin doit être postérieure à celle de début"
                    ),
                }
            )

    def __str__(self):
        return "{person} : {tag_label} {range}".format(
            person=str(self.person),
            tag_label=self.qualification.label,
            range=self.get_range_display(),
        )

    class Meta:
        verbose_name = _("statut d'une personne")
        verbose_name_plural = _("statuts")


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
