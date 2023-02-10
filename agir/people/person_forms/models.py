from collections import OrderedDict
from itertools import chain

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import JSONField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from agir.lib import html
from agir.lib.form_fields import CustomJSONEncoder
from agir.lib.models import DescriptionField, TimeStampedModel

__all__ = ["PersonForm", "PersonFormSubmission"]


GOOGLE_SHEET_REGEX = r"^https://docs.google.com/spreadsheets/d/(?P<sid>[A-Za-z0-9_-]{40,})/.*[?#&]gid=(?P<gid>[0-9]+)"


class PersonFormQueryset(models.QuerySet):
    def published(self):
        return self.filter(models.Q(published=True))

    def open(self):
        now = timezone.now()
        return self.published().filter(
            (models.Q(start_time__isnull=True) | models.Q(start_time__lt=now))
            & (models.Q(end_time__isnull=True) | models.Q(end_time__gt=now))
        )


def default_custom_forms():
    return [
        {
            "title": "Mes informations",
            "fields": [
                {"id": "first_name", "person_field": True},
                {"id": "last_name", "person_field": True},
            ],
        }
    ]


class PersonForm(TimeStampedModel):
    objects = PersonFormQueryset.as_manager()

    title = models.CharField(_("Titre"), max_length=250)
    slug = models.SlugField(_("Slug"), max_length=50, unique=True)
    published = models.BooleanField(_("Publié"), default=True)

    result_url_uuid = models.UUIDField(
        "UUID pour l'affichage des résultats", editable=False, null=True
    )

    start_time = models.DateTimeField(
        _("Date d'ouverture du formulaire"), null=True, blank=True
    )
    end_time = models.DateTimeField(
        _("Date de fermeture du formulaire"), null=True, blank=True
    )

    editable = models.BooleanField(
        _("Les répondant⋅e⋅s peuvent modifier leurs réponses"), default=False
    )

    allow_anonymous = models.BooleanField(
        _("Les répondant⋅es n'ont pas besoin d'être connecté⋅es"), default=False
    )

    send_answers_to = models.EmailField(
        _("Envoyer les réponses par email à une adresse email (facultatif)"), blank=True
    )

    description = DescriptionField(
        _("Description"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Description visible en haut de la page de remplissage du formulaire"
        ),
    )

    short_description = models.CharField(
        _("Description courte"),
        default=str(),
        null=False,
        blank=True,
        max_length=255,
        help_text=_(
            "Description visible lors du partage sur les réseaux sociaux et lors des envois de rappels par notification"
        ),
    )

    send_confirmation = models.BooleanField(
        _("Envoyer une confirmation par email"),
        default=False,
        help_text="Envoyer le contenu de la note après complétion par email, en plus de le montrer à l'utilisateur.",
    )

    confirmation_note = DescriptionField(
        _("Note après complétion"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Note montrée (et éventuellement envoyée par email) à l'utilisateur une fois le formulaire validé."
        ),
    )
    before_message = DescriptionField(
        _("Note avant ouverture"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Note montrée à l'utilisateur qui essaye d'accéder au formulaire avant son ouverture."
        ),
        blank=True,
    )

    after_message = DescriptionField(
        _("Note de fermeture"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Note montrée à l'utilisateur qui essaye d'accéder au formulaire après sa date de fermeture."
        ),
        blank=True,
    )

    required_tags = models.ManyToManyField(
        "PersonTag",
        related_name="authorized_forms",
        related_query_name="authorized_form",
        blank=True,
    )

    segment = models.ForeignKey(
        "mailing.Segment",
        on_delete=models.SET_NULL,
        related_name="person_forms",
        related_query_name="person_form",
        blank=True,
        null=True,
    )

    unauthorized_message = DescriptionField(
        _("Note pour les personnes non autorisées"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Note montrée à tout utilisateur qui n'aurait pas le tag nécessaire pour afficher le formulaire."
        ),
        blank=True,
    )

    main_question = models.CharField(
        _("Intitulé de la question principale"),
        max_length=200,
        help_text=_("Uniquement utilisée si des choix de tags sont demandés."),
        blank=True,
    )
    tags = models.ManyToManyField(
        "PersonTag", related_name="forms", related_query_name="form", blank=True
    )

    custom_fields = JSONField(_("Champs"), blank=False, default=default_custom_forms)

    config = JSONField(_("Configuration"), blank=True, default=dict)

    campaign_template = models.ForeignKey(
        "nuntius.Campaign",
        verbose_name="Créer une campagne à partir de ce modèle",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )

    lien_feuille_externe = models.URLField(
        verbose_name="Lien vers une feuille de calcul externe",
        blank=True,
        help_text="Une feuille de calcul externe (Google Sheet uniquement pour moment) qui sera mise à jour avec les"
        " réponses au formulaire. Attention, cette feuille sera écrasée au fur et à mesure.",
        validators=[
            RegexValidator(
                regex=GOOGLE_SHEET_REGEX,
                message="Indiquez-ici l'URL complète vers la feuille Google sheet à modifier. La feuille doit être"
                " accessible et modifiable pour toute personne avec le lien.",
            )
        ],
    )

    @property
    def submit_label(self):
        return self.config.get("submit_label", "Envoyer")

    @property
    def fields_dict(self):
        return OrderedDict(
            (field["id"], field)
            for field in chain(
                (
                    field
                    for fieldset in self.custom_fields
                    for field in fieldset.get("fields", [])
                ),
                self.config.get("hidden_fields", []),
            )
        )

    @property
    def is_open(self):
        now = timezone.now()
        return (self.start_time is None or self.start_time < now) and (
            self.end_time is None or now < self.end_time
        )

    def is_authorized(self, person):
        return (
            not self.required_tags.all()
            or (person.tags.all() & self.required_tags.all()).exists()
        ) and (
            self.segment is None
            or (person is not None and self.segment.is_subscriber(person))
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

    @property
    def meta_description(self):
        if self.short_description:
            return self.short_description
        if self.description:
            return html.textify(self.description)
        return ""

    def __str__(self):
        return "« {} »".format(self.title)

    class Meta:
        verbose_name = _("Formulaire")
        ordering = ("-created",)


class PersonFormSubmission(
    ExportModelOperationsMixin("person_form_submission"), TimeStampedModel
):
    form = models.ForeignKey(
        "PersonForm",
        on_delete=models.CASCADE,
        related_name="submissions",
        editable=False,
    )
    person = models.ForeignKey(
        "Person",
        on_delete=models.CASCADE,
        related_name="form_submissions",
        null=True,
        blank=True,
    )

    data = JSONField(_("Données"), default=dict, encoder=CustomJSONEncoder)

    def __str__(self):
        return f"{self.form.title} : réponse de {str(self.person)}"
