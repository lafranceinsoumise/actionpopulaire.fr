from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

from lib.models import APIResource, LocationMixin, AbstractLabel


class PersonManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a person with the given username, email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create a user 
        :param email: the user's email
        :param password: optional password that may be used to connect to the adimn website
        :param extra_fields: any other field
        :return: 
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
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

        return self._create_user(email, password, **extra_fields)


class Person(APIResource, AbstractBaseUser, PermissionsMixin, LocationMixin):
    """
    Model that represents a physical person that signed as a JLM2017 supporter
    
    A person is identified by the email address he's signed up with.
    He is associated with permissions that determine what he can and cannot do
    with the API.
    
    He has an optional password, which will be only used to authenticate him with
    the API admin.
    """
    objects = PersonManager()

    email = models.EmailField(
        _('adresse email'),
        unique=True,
        blank=False,
        help_text=_("L'adresse email de la personne, utilisée comme identifiant")
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
        help_text=_("Si des mails ont été rejetés, indique la date du dernier rejet")
    )

    tags = models.ManyToManyField('PersonTag', related_name='people', blank=True)

    is_staff = models.BooleanField(
        _('est staff'),
        default=False,
        help_text=_("Indique si l'utilisateur peut se connecter au site admin."),
    )
    is_active = models.BooleanField(
        _('est actif'),
        default=True,
        help_text=_(
            'Indique si la personne devrait être traitée comme active. '
            'Désélectionnez cette option plutôt que de supprimer la personne.'
        ),
    )


    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('personne')
        verbose_name_plural = _('personnes')

    def __str__(self):
        return self.name


class PersonTag(AbstractLabel):
    """
    Model that represents a tag that may be used to qualify people
    """
    class Meta:
        verbose_name = _('tag')