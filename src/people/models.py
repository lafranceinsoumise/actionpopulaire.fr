from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager

from lib.models import BaseAPIResource, LocationMixin, AbstractLabel, NationBuilderResource
from authentication.models import Role


class PersonManager(models.Manager):
    def get_by_natural_key(self, email):
        return self.select_related('role').get(email=email)

    def _create_person(self, email, password, *, is_staff, is_superuser, is_active=True, **extra_fields):
        """
        Creates and saves a person with the given username, email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = BaseUserManager.normalize_email(email)

        role = Role(type=Role.PERSON_ROLE, is_staff=is_staff, is_superuser=is_superuser, is_active=is_active)
        role.set_password(password)

        with transaction.atomic():
            role.save()

            person = self.model(email=email, role=role, **extra_fields)
            person.save(using=self._db)

        return person

    def create_person(self, email, password=None, **extra_fields):
        """
        Create a user 
        :param email: the user's email
        :param password: optional password that may be used to connect to the adimn website
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

    email = models.EmailField(
        _('adresse email'),
        unique=True,
        blank=False,
        help_text=_("L'adresse email de la personne, utilisée comme identifiant")
    )

    subscribed = models.BooleanField(
        _('inscrit à la newsletter'),
        default=True,
        blank=True,
        help_text=_("L'utilisateur souhaite-t-il recevoir les newsletters ?")
    )

    first_name = models.CharField(_('prénom'), max_length=255, blank=True)
    last_name = models.CharField(_('nom de famille'), max_length=255, blank=True)

    bounced = models.BooleanField(
        _('email rejeté'),
          default=False,
        help_text=_("Indique que des mails envoyés ont été rejetés par le serveur distant")
    )
    bounced_date = models.DateTimeField(
        _("date de rejet de l'email"),
        null=True,
        blank=True,
        help_text=_("Si des mails ont été rejetés, indique la date du dernier rejet")
    )

    tags = models.ManyToManyField('PersonTag', related_name='people', blank=True)

    class Meta:
        verbose_name = _('personne')
        verbose_name_plural = _('personnes')
        ordering = ('email',)
        # add permission 'view'
        default_permissions = ('add', 'change', 'delete', 'view')

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name or self.email


class PersonTag(AbstractLabel):
    """
    Model that represents a tag that may be used to qualify people
    """
    class Meta:
        verbose_name = _('tag')
