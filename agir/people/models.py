import warnings
from django.db import models, transaction
from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from agir.lib.models import BaseAPIResource, LocationMixin, AbstractLabel, NationBuilderResource, DescriptionField
from agir.authentication.models import Role
from . import metrics

from .model_fields import MandatesField


class PersonManager(models.Manager):
    def get(self, *args, **kwargs):
        if 'email' in kwargs:
            kwargs['emails__address'] = kwargs['email']
            del kwargs['email']
        return super().get(*args, **kwargs)

    def create(self, *args, **kwargs):
        warnings.warn('You shoud use create_person or create_superperson.', DeprecationWarning)
        if 'email' not in kwargs:
            raise ValueError('Email must be set')
        email = kwargs.pop('email')
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        person = self._create_person(email, kwargs.get('password', None), **kwargs)

        return person

    def get_by_natural_key(self, email):
        email_field_class = self.model.emails.rel.related_model
        try:
            return email_field_class.objects.get_by_natural_key(email).person
        except email_field_class.DoesNotExist:
            raise self.model.DoesNotExist

    def _create_person(self, email, password, *, is_staff, is_superuser, is_active=True, **extra_fields):
        """
        Creates and saves a person with the given username, email and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        role = Role(type=Role.PERSON_ROLE, is_staff=is_staff, is_superuser=is_superuser, is_active=is_active)
        role.set_password(password)

        with transaction.atomic():
            role.save()

            person = self.model(role=role, **extra_fields)
            person.save(using=self._db)

            person.add_email(email)

        if not settings.MAILTRAIN_DISABLE:
            from .tasks import update_mailtrain
            update_mailtrain.delay(person.pk)

        return person

    def create_person(self, email, password=None, **extra_fields):
        """
        Create a user
        :param email: the user's email
        :param password: optional password that may be used to connect to the admin website
        :param extra_fields: any other field
        :return:
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_person(email, password, **extra_fields)

    def create_superperson(self, email, password, **extra_fields):
        """
        Create a superuser
        :param email:
        :param password:
        :param extra_fields:
        :return:
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_person(email, password, **extra_fields)


class Person(BaseAPIResource, NationBuilderResource, LocationMixin):
    """
    Model that represents a physical person that signed as a JLM2017 supporter

    A person is identified by the email address he's signed up with.
    He is associated with permissions that determine what he can and cannot do
    with the API.

    He has an optional password, which will be only used to authenticate him with
    the API admin.
    """
    objects = PersonManager()

    role = models.OneToOneField('authentication.Role', on_delete=models.PROTECT, related_name='person')

    subscribed = models.BooleanField(
        _("Recevoir les lettres d'information"),
        default=True,
        blank=True,
        help_text=_("Vous recevrez les lettres de la France insoumise, notamment : les lettres d'information, les"
                    " appels à volontaires, les annonces d'émissions ou d'événements...")
    )

    event_notifications = models.BooleanField(
        _('Recevoir les notifications des événements'),
        default=True,
        blank=True,
        help_text=_("Vous recevrez des messages quand les informations des évènements auxquels vous souhaitez participer"
                    " sont mis à jour ou annulés.")
    )

    group_notifications = models.BooleanField(
        _('Recevoir les notifications de mes groupes'),
        default=True,
        blank=True,
        help_text=_("Vous recevrez des messages quand les informations du groupe change, ou quand le groupe organise des"
                    " événements.")
    )

    draw_participation = models.BooleanField(
        _('Participer aux tirages au sort'),
        default=False,
        blank=True,
        help_text=_("Vous pourrez être tiré⋅e au sort parmis les Insoumis⋅es pour participer à des événements comme la Convention."
                    "Vous aurez la possibilité d'accepter ou de refuser cette participation.")
    )

    first_name = models.CharField(_('prénom'), max_length=255, blank=True)
    last_name = models.CharField(_('nom de famille'), max_length=255, blank=True)

    tags = models.ManyToManyField('PersonTag', related_name='people', blank=True)

    contact_phone = PhoneNumberField(_("Numéro de téléphone de contact"), blank=True)

    GENDER_FEMALE = 'F'
    GENDER_MALE = 'M'
    GENDER_OTHER = 'O'
    GENDER_CHOICES = (
        (GENDER_FEMALE, _('Femme')),
        (GENDER_MALE, _('Homme')),
        (GENDER_OTHER, _('Autre/Non défini'))
    )
    gender = models.CharField(_('Genre'), max_length=1, blank=True, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(_('Date de naissance'), null=True, blank=True)

    mandates = MandatesField(_('Mandats électoraux'), default=list, blank=True)

    meta = JSONField(_('Autres données'), default=dict, blank=True)

    search = SearchVectorField('Données de recherche', editable=False, null=True)

    class Meta:
        verbose_name = _('personne')
        verbose_name_plural = _('personnes')
        ordering = ('-created',)
        # add permission 'view'
        default_permissions = ('add', 'change', 'delete', 'view')
        indexes = (
            GinIndex(fields=['search'], name='search_index'),
        )

    def save(self, *args, **kwargs):
        if self._state.adding:
            metrics.subscriptions.inc()

        return super().save(*args, **kwargs)

    def __str__(self):
        if self.first_name and self.last_name:
            return "{} {} <{}>".format(self.first_name, self.last_name, self.email)
        else:
            return self.email

    @property
    def email(self):
        return self.primary_email.address if self.primary_email else ''

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
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name or self.email

    def add_email(self, email_address, **kwargs):
        try:
            email = self.emails.get_by_natural_key(email_address)
            email.bounced = kwargs['bounced'] if kwargs.get('bounced', None) is not None else email.bounced
            email.bounced_date = kwargs['bounced_date'] if kwargs.get('bounced_date', None) is not None else email.bounced_date
            email.save()
        except ObjectDoesNotExist:
            PersonEmail.objects.create_email(address=email_address, person=self, **kwargs)

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


class PersonTag(AbstractLabel):
    """
    Model that represents a tag that may be used to qualify people
    """

    exported = models.BooleanField(_('Exporté vers mailtrain'), default=False)

    class Meta:
        verbose_name = _('tag')


class PersonEmailManager(models.Manager):
    @classmethod
    def normalize_email(cls, email, *, lowercase_local_part=True):
        try:
            local_part, domain = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([local_part.lower() if lowercase_local_part else local_part, domain.lower()])
        return email

    def create_email(self, address, person, *, lowercase_local_part=True, **kwargs):
        return self.create(
            address=self.normalize_email(address, lowercase_local_part=lowercase_local_part),
            person=person,
            **kwargs
        )

    def get_by_natural_key(self, address):
        # look first without lowercasing email
        try:
            return self.get(address=self.normalize_email(address, lowercase_local_part=False))
        # if it does not exist, lowercase it
        except self.model.DoesNotExist:
            return self.get(address=self.normalize_email(address, lowercase_local_part=True))


class PersonEmail(models.Model):
    """
    Model that represent a person email address
    """
    objects = PersonEmailManager()

    address = models.EmailField(
        _('adresse email'),
        unique=True,
        blank=False,
        help_text=_("L'adresse email de la personne, utilisée comme identifiant")
    )

    _bounced = models.BooleanField(
        _('email rejeté'),
        default=False,
        db_column='bounced',
        help_text=_("Indique que des mails envoyés ont été rejetés par le serveur distant")
    )

    bounced_date = models.DateTimeField(
        _("date de rejet de l'email"),
        null=True,
        blank=True,
        help_text=_("Si des mails ont été rejetés, indique la date du dernier rejet")
    )

    @property
    def bounced(self):
        return self._bounced

    @bounced.setter
    def bounced(self, value):
        if value and self._bounced is False:
            self.bounced_date = timezone.now()
        self._bounced = value

    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=False, related_name='emails')

    class Meta:
        order_with_respect_to = 'person'
        verbose_name = _("Email")

    def __str__(self):
        return self.address

    def clean(self):
        self.address = PersonEmail.objects.normalize_email(self.address)


class PersonFormQueryset(models.QuerySet):
    def published(self):
        return self.filter(
            models.Q(published=True)
        )

    def open(self):
        now = timezone.now()
        return self.published().filter(
            (models.Q(start_time__isnull=True) | models.Q(start_time__lt=now)) &
            (models.Q(end_time__isnull=True) | models.Q(end_time__gt=now))
        )


class PersonForm(TimeStampedModel):
    objects = PersonFormQueryset.as_manager()

    title = models.CharField(_('Titre'), max_length=250)
    slug = models.SlugField(_('Slug'), max_length=50)
    published = models.BooleanField(_('Publié'), default=True)

    start_time = models.DateTimeField(_("Date d'ouverture du formulaire"), null=True, blank=True)
    end_time = models.DateTimeField(_("Date de fermeture du formulaire"), null=True, blank=True)

    description = DescriptionField(
        _('Description'),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Description visible en haut de la page de remplissage du formulaire"
        ),
    )

    send_confirmation = models.BooleanField(_("Envoyer une confirmation par email"), default=False)

    confirmation_note = DescriptionField(
        _('Note après complétion'),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Note montrée (et éventuellement envoyée par email) à l'utilisateur une fois le formulaire validé."
        )
    )
    before_message = DescriptionField(
        _("Note avant ouverture"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=(
            "Note montrée à l'utilisateur qui essaye d'accéder au formulaire avant son ouverture."
        ),
        blank=True
    )

    after_message = DescriptionField(
        _("Note de fermeture"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=(
            "Note montrée à l'utilisateur qui essaye d'accéder au formulaire après sa date de fermeture."
        ),
        blank=True
    )

    main_question = models.CharField(_("Intitulé de la question principale"), max_length=200,
                                     help_text=_('Uniquement utilisée si des choix de tags sont demandés.'), blank=True)
    tags = models.ManyToManyField('PersonTag', related_name='forms', related_query_name='form', blank=True)

    custom_fields = JSONField(_('Champs'), blank=False, default=list)

    @property
    def fields_dict(self):
        return {field['id']: field for fieldset in self.custom_fields for field in fieldset['fields']}

    @property
    def is_open(self):
        now = timezone.now()
        return (
            (self.start_time is None or self.start_time < now) and (self.end_time is None or now < self.end_time)
        )

    @property
    def html_closed_message(self):
        now = timezone.now()
        if self.start_time is not None and self.start_time > now:
            if self.before_message:
                return self.html_before_message()
            else:
                return "Ce formulaire n'est pas encore ouvert."
        else:
            if self.after_message:
                return self.html_after_message()
            else:
                return "Ce formulaire est maintenant fermé."

    def get_form(self):
        from .forms import get_people_form_class
        return get_people_form_class(self)

    def __str__(self):
        return "« {} »".format(self.title)

    class Meta:
        verbose_name = _("Formulaire")


class PersonFormSubmission(TimeStampedModel):
    form = models.ForeignKey('PersonForm', on_delete=models.CASCADE, related_name='submissions', editable=False)
    person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='form_submissions', editable=False)

    data = JSONField(_('Données'), editable=False)
