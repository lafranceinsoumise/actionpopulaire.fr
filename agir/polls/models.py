import uuid

import markdown
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from agir.lib.models import BaseAPIResource


class Poll(BaseAPIResource):
    title = models.CharField(_("Titre de la consultation"), max_length=255)
    description = models.TextField(
        _("Description de la consultation"),
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
            "Un object JSON décrivant les règles. Actuellement, sont reconnues `options`,"
            "`min_options`, `max_options` et `verified_user`"
        ),
        default=dict,
    )
    tags = models.ManyToManyField(
        "people.PersonTag", related_name="polls", related_query_name="poll", blank=True
    )

    def make_choice(self, person, options):
        with transaction.atomic():
            if self.tags.all().count() > 0:
                person.tags.add(*self.tags.all())
            PollChoice.objects.create(
                person=person, poll=self, selection=[option.pk for option in options]
            )

    def html_description(self):
        return mark_safe(markdown.markdown(self.description))

    def __str__(self):
        return self.title


class PollOption(BaseAPIResource):
    description = models.TextField(
        _("Option"), help_text=_("Option telle qu'elle apparaîtra aux insoumis⋅es.")
    )
    poll = models.ForeignKey("Poll", on_delete=models.CASCADE, related_name="options")

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
    selection = JSONField(encoder=DjangoJSONEncoder)
    anonymous_id = models.UUIDField(_("Identifiant anonyme"), default=uuid.uuid4)

    class Meta:
        unique_together = (("person", "poll"),)
