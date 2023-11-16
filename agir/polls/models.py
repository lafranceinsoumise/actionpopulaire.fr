import uuid

import markdown
from agir.lib.form_fields import CustomJSONEncoder
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.db.models import JSONField
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from agir.lib.models import BaseAPIResource, DescriptionField

__all__ = ["Poll", "PollOption", "PollChoice"]


class Poll(BaseAPIResource):
    title = models.CharField(_("Titre de la consultation"), max_length=255)
    description = DescriptionField(
        _("Description de la consultation"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_("Le texte de description affiché pour tous les insoumis"),
    )
    start = models.DateTimeField(
        _("Date et heure de début de la consultation"),
        help_text=_("La consultation sera automatiquement ouverte à ce moment"),
    )
    end = models.DateTimeField(
        _("Date et heure de fin de la consultation"),
        help_text=_("La consultation sera automatiquement fermée à ce moment"),
    )
    rules = JSONField(
        _("Les règles du vote"),
        encoder=DjangoJSONEncoder,
        help_text=_(
            "Un object JSON décrivant les règles. Actuellement, sont reconnues `success_url`, `verified_user`, "
            "`confirmation_email`, `options`, `min_options`, `max_options`, `shuffle` et `option_groups`"
        ),
        default=dict,
    )
    tags = models.ManyToManyField(
        "people.PersonTag",
        related_name="polls",
        related_query_name="poll",
        blank=True,
        verbose_name="Tag à ajouter aux participant⋅es",
    )

    confirmation_note = DescriptionField(
        "Note après participation",
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Note montrée à l'utilisateur une fois la participation enregistrée."
        ),
        blank=True,
    )

    authorized_segment = models.ForeignKey(
        "mailing.Segment",
        on_delete=models.SET_NULL,
        related_name="+",
        related_query_name="+",
        blank=True,
        null=True,
        verbose_name="Limiter l'accès à la consultation à ce segment",
    )

    unauthorized_message = DescriptionField(
        _("Note pour les personnes non autorisées"),
        allowed_tags=settings.ADMIN_ALLOWED_TAGS,
        help_text=_(
            "Note montrée à tout utilisateur qui n'aurait pas le tag nécessaire pour afficher le formulaire."
        ),
        blank=True,
        default="",
    )

    def make_choice(self, person, selection):
        with transaction.atomic():
            if self.tags.all().count() > 0:
                person.tags.add(*self.tags.all())

            return PollChoice.objects.create(
                person=person, poll=self, selection=selection
            )

    def html_description(self):
        return mark_safe(markdown.markdown(self.description))

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-start",)


class PollOption(BaseAPIResource):
    DEFAULT_OPTION_GROUP_ID = "choice"

    description = models.TextField(
        _("Option"), help_text=_("Option telle qu'elle apparaîtra aux insoumis⋅es.")
    )
    poll = models.ForeignKey("Poll", on_delete=models.CASCADE, related_name="options")
    option_group_id = models.CharField(
        _("Identifiant du groupe d'options"),
        null=False,
        blank=False,
        default=DEFAULT_OPTION_GROUP_ID,
        max_length=200,
        help_text=_(
            "Identifiant d'un groupe qui permettra de regrouper plusieurs options ensemble et definir une "
            "configuration spécifique"
        ),
    )

    def html_description(self):
        return mark_safe(markdown.markdown(self.description))

    def __str__(self):
        return self.html_description()


class PollChoice(ExportModelOperationsMixin("poll_choice"), BaseAPIResource):
    person = models.ForeignKey(
        "people.Person",
        on_delete=models.SET_NULL,
        null=True,
        related_name="poll_choices",
    )
    poll = models.ForeignKey("Poll", on_delete=models.CASCADE)
    selection = JSONField(encoder=CustomJSONEncoder)
    anonymous_id = models.UUIDField(_("Identifiant anonyme"), default=uuid.uuid4)

    def parse_selection(self):
        selection = self.selection

        if isinstance(self.selection, list):
            # Account for legacy poll choices where only one option group was allowed and selection was a JSON array
            selection = {PollOption.DEFAULT_OPTION_GROUP_ID: self.selection}

        return {
            key: list(
                PollOption.objects.filter(id__in=choices).values_list(
                    "description", flat=True
                )
            )
            for key, choices in selection.items()
        }

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("person", "poll"),
                name="unique_person_and_poll",
            ),
        )
