from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import ugettext_lazy as _

from lib.models import BaseAPIResource


class Poll(BaseAPIResource):
    title = models.CharField(
        _('Titre de la consultation'),
        max_length=255,
    )
    description = models.TextField(
        _('Description de la consultation'),
        help_text=_('Le texte de description affiché pour tous les insoumis'),
    )
    start = models.DateTimeField(
        _('Date et heure de début de la consultation'),
        help_text=_('La consultation sera automatiquement ouverte à ce moment'),
    )
    end = models.DateTimeField(
        _('Date et heure de fin de la consultation'),
        help_text=_('La consultation sera automatiquement fermée à ce moment'),
    )
    rules = JSONField(
        _('Les règles du vote'),
        encoder=DjangoJSONEncoder,
        help_text=_('Un object JSON décrivant les règles. Actuellement, sont reconnues `min_options` et'
                    '`max_options'),
        default=dict
    )

    def make_choice(self, person, options):
        PollChoice.objects.create(person=person, poll=self, selection=[option.pk for option in options])


class PollOption(BaseAPIResource):
    description = models.TextField(
        _("Option"),
        help_text=_("Option telle qu'elle apparaîtra aux insoumis⋅es."),
    )
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE, related_name='options')

    def __str__(self):
        return self.description


class PollChoice(BaseAPIResource):
    person = models.ForeignKey('people.Person')
    poll = models.ForeignKey('Poll', on_delete=models.CASCADE)
    selection = JSONField(encoder=DjangoJSONEncoder)
