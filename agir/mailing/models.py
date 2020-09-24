from functools import reduce

from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django.db.models import Q, Sum
from django_countries.fields import CountryField
from nuntius.models import BaseSegment, CampaignSentStatusType

from agir.events.models import RSVP
from agir.groups.models import Membership
from agir.lib import data
from agir.lib.model_fields import ChoiceArrayField
from agir.payments.model_fields import AmountField
from agir.payments.models import Subscription, Payment
from agir.people.models import Person

DATE_HELP_TEXT = (
    "Écrivez en toute lettre JJ/MM/AAAA plutôt qu'avec le widget, ça ira plus vite."
)

DONATION_FILTER = {
    "payments__type__startswith": "don",
    "payments__status": Payment.STATUS_COMPLETED,
}


class Segment(BaseSegment, models.Model):
    GA_STATUS_NOT_MEMBER = "N"
    GA_STATUS_MEMBER = "m"
    GA_STATUS_MANAGER = "M"
    GA_STATUS_REFERENT = "R"
    GA_STATUS_CHOICES = (
        (GA_STATUS_NOT_MEMBER, "Non membres de GA"),
        (GA_STATUS_MEMBER, "Membres de GA"),
        (GA_STATUS_MANAGER, "Animateurices et gestionnaires de GA"),
        (GA_STATUS_REFERENT, "Animateurices de GA"),
    )

    name = models.CharField("Nom", max_length=255)

    tags = models.ManyToManyField("people.PersonTag", blank=True)
    force_non_insoumis = models.BooleanField(
        "Envoyer y compris aux non insoumis",
        default=False,
        help_text="Inclut par exemple les ancien⋅es donateurices non inscrits sur la plateforme. À utiliser uniquement si vous savez très bien ce que vous faites.",
    )
    supportgroup_status = models.CharField(
        "Limiter aux membres de groupes ayant ce statut",
        max_length=1,
        choices=GA_STATUS_CHOICES,
        blank=True,
    )
    supportgroup_subtypes = models.ManyToManyField(
        "groups.SupportGroupSubtype",
        verbose_name="Limiter aux membres de groupes d'un de ces sous-types",
        blank=True,
    )
    events = models.ManyToManyField(
        "events.Event",
        verbose_name="Limiter aux participant⋅e⋅s à un des événements",
        blank=True,
    )
    events_subtypes = models.ManyToManyField(
        "events.EventSubtype",
        verbose_name="Limiter aux participant⋅e⋅s à un événements de ce type",
        blank=True,
    )
    events_start_date = models.DateTimeField(
        "Limiter aux participant⋅e⋅s à des événements commençant après cette date",
        blank=True,
        null=True,
    )
    events_end_date = models.DateTimeField(
        "Limiter aux participant⋅e⋅s à des événements terminant avant cette date",
        blank=True,
        null=True,
    )
    events_organizer = models.BooleanField(
        "Limiter aux organisateurices (sans effet si pas d'autres filtres événements)",
        blank=True,
        default=False,
    )

    forms = models.ManyToManyField(
        "people.PersonForm",
        verbose_name="A répondu à au moins un de ces formulaires",
        blank=True,
        related_name="+",
    )

    polls = models.ManyToManyField(
        "polls.Poll",
        verbose_name="A participé à au moins une de ces consultations",
        blank=True,
        related_name="+",
    )

    countries = CountryField("Limiter aux pays", multiple=True, blank=True)
    departements = ChoiceArrayField(
        models.CharField(choices=data.departements_choices, max_length=3),
        verbose_name="Limiter aux départements (calcul à partir du code postal)",
        default=list,
        blank=True,
    )
    area = MultiPolygonField(
        "Limiter à un territoire définit manuellement", blank=True, null=True
    )

    campaigns = models.ManyToManyField(
        "nuntius.Campaign",
        related_name="+",
        verbose_name="Limiter aux personnes ayant reçu une des campagnes",
        blank=True,
    )

    last_open = models.DurationField(
        "Limiter aux personnes ayant ouvert un email envoyé au court de la durée indiquée",
        blank=True,
        null=True,
    )

    last_click = models.DurationField(
        "Limiter aux personnes ayant cliqué dans un email envoyé au court de la durée indiquée",
        blank=True,
        null=True,
    )

    FEEDBACK_OPEN = 1
    FEEDBACK_CLICKED = 2
    FEEDBACK_NOT_OPEN = 3
    FEEDBACK_NOT_CLICKED = 4
    FEEDBACK_OPEN_NOT_CLICKED = 5
    FEEDBACK_CHOICES = (
        (FEEDBACK_OPEN, "Personnes ayant ouvert"),
        (FEEDBACK_CLICKED, "Personnes ayant cliqué"),
        (FEEDBACK_NOT_OPEN, "Personnes n'ayant pas ouvert"),
        (FEEDBACK_NOT_CLICKED, "Personnes n'ayant pas cliqué"),
        (FEEDBACK_OPEN_NOT_CLICKED, "Personnes ayant ouvert mais pas cliqué"),
    )

    campaigns_feedback = models.PositiveSmallIntegerField(
        "Limiter en fonction de la réaction à ces campagnes",
        blank=True,
        null=True,
        choices=FEEDBACK_CHOICES,
        help_text="Aucun effet si aucune campagne n'est sélectionnée dans le champ précédent",
    )

    registration_date = models.DateTimeField(
        "Limiter aux membres inscrit⋅e⋅s après cette date", blank=True, null=True
    )
    last_login = models.DateTimeField(
        "Limiter aux membres s'étant connecté⋅e pour la dernière fois après cette date",
        blank=True,
        null=True,
    )

    gender = models.CharField(
        "Genre", max_length=1, blank=True, choices=Person.GENDER_CHOICES
    )

    born_after = models.DateField(
        "Personnes nées après le", blank=True, null=True, help_text=DATE_HELP_TEXT
    )
    born_before = models.DateField(
        "Personnes nées avant le", blank=True, null=True, help_text=DATE_HELP_TEXT
    )

    donation_after = models.DateField(
        "A fait au moins un don (don mensuel inclus) après le",
        blank=True,
        null=True,
        help_text=DATE_HELP_TEXT,
    )
    donation_not_after = models.DateField(
        "N'a pas fait de don (don mensuel inclus) depuis le",
        blank=True,
        null=True,
        help_text=DATE_HELP_TEXT,
    )
    donation_total_min = AmountField(
        "Montant total des dons supérieur ou égal à", blank=True, null=True
    )
    donation_total_max = AmountField(
        "Montant total des dons inférieur ou égal à", blank=True, null=True
    )
    donation_total_range = DateRangeField(
        "Pour le filtre de montant total, prendre uniquement en compte les dons entre ces deux dates",
        blank=True,
        null=True,
        help_text="Écrire sous la forme JJ/MM/AAAA. La date de début est incluse, pas la date de fin.",
    )

    subscription = models.BooleanField(
        "A une souscription mensuelle active", blank=True, null=True
    )

    exclude_segments = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="+",
        verbose_name="Exclure les personnes membres des segments suivants",
        blank=True,
    )

    add_segments = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="+",
        verbose_name="Ajouter les personnes membres des segments suivants",
        blank=True,
    )

    def get_subscribers_q(self):
        q = Q(subscribed=True, emails___bounced=False)

        if not self.force_non_insoumis:
            q = q & Q(is_insoumise=True)

        if self.tags.all().count() > 0:
            q = q & Q(tags__in=self.tags.all())

        if self.supportgroup_status:
            if self.supportgroup_status == self.GA_STATUS_NOT_MEMBER:
                supportgroup_q = ~Q(memberships__supportgroup__published=True)
            elif self.supportgroup_status == self.GA_STATUS_MEMBER:
                supportgroup_q = Q(memberships__supportgroup__published=True)

            elif self.supportgroup_status == self.GA_STATUS_REFERENT:
                supportgroup_q = Q(
                    memberships__supportgroup__published=True,
                    memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
                )
            else:
                # ==> self.supportgroup_status == self.GA_STATUS_MANAGER
                supportgroup_q = Q(
                    memberships__supportgroup__published=True,
                    memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
                )

            if self.supportgroup_subtypes.all().count() > 0:
                supportgroup_q = supportgroup_q & Q(
                    memberships__supportgroup__subtypes__in=self.supportgroup_subtypes.all()
                )

            q = q & supportgroup_q

        events_filter = {}

        if self.events.all().count() > 0:
            events_filter["in"] = self.events.all()

        if self.events_subtypes.all().count() > 0:
            events_filter["subtype__in"] = self.events_subtypes.all()

        if self.events_start_date is not None:
            events_filter["start_time__gt"] = self.events_start_date

        if self.events_end_date is not None:
            events_filter["end_time__lt"] = self.events_end_date

        if events_filter:
            prefix = "organized_events" if self.events_organizer else "rsvps__event"
            q = q & Q(**{f"{prefix}__{k}": v for k, v in events_filter.items()})

            if not self.events_organizer:
                q = q & Q(
                    rsvps__status__in=[
                        RSVP.STATUS_CONFIRMED,
                        RSVP.STATUS_AWAITING_PAYMENT,
                    ]
                )

        if self.forms.all().count() > 0:
            q = q & Q(form_submissions__form__in=self.forms.all())

        if self.polls.all().count() > 0:
            q = q & Q(poll_choices__poll__in=self.polls.all())

        if self.campaigns.all().count() > 0:
            if self.campaigns_feedback == self.FEEDBACK_OPEN:
                campaign__kwargs = {"campaignsentevent__open_count__gt": 0}
            elif self.campaigns_feedback == self.FEEDBACK_CLICKED:
                campaign__kwargs = {"campaignsentevent__click_count__gt": 0}
            elif self.campaigns_feedback == self.FEEDBACK_NOT_OPEN:
                campaign__kwargs = {"campaignsentevent__open_count": 0}
            elif self.campaigns_feedback == self.FEEDBACK_NOT_CLICKED:
                campaign__kwargs = {"campaignsentevent__click_count": 0}
            elif self.campaigns_feedback == self.FEEDBACK_OPEN_NOT_CLICKED:
                campaign__kwargs = {
                    "campaignsentevent__open_count__gt": 1,
                    "campaignsentevent__click_count": 0,
                }
            else:
                campaign__kwargs = {}

            q = q & Q(
                campaignsentevent__result__in=[
                    CampaignSentStatusType.UNKNOWN,
                    CampaignSentStatusType.OK,
                ],
                campaignsentevent__campaign__in=self.campaigns.all(),
                **campaign__kwargs,
            )

        if self.last_open is not None:
            q = q & Q(
                campaignsentevent__open_count__gt=0,
                campaignsentevent__datetime__gt=self.last_open,
            )

        if self.last_click is not None:
            q = q & Q(
                campaignsentevent__click_count__gt=0,
                campaignsentevent__datetime__gt=self.last_click,
            )

        if len(self.countries) > 0:
            q = q & Q(location_country__in=self.countries)

        if len(self.departements) > 0:
            q = q & Q(data.filtre_departements(*self.departements))

        if self.area is not None:
            q = q & Q(coordinates__intersects=self.area)

        if self.registration_date is not None:
            q = q & Q(created__gt=self.registration_date)

        if self.last_login is not None:
            q = q & Q(role__last_login__gt=self.last_login)

        if self.gender:
            q = q & Q(gender=self.gender)

        if self.born_after is not None:
            q = q & Q(date_of_birth__gt=self.born_after)

        if self.born_before is not None:
            q = q & Q(date_of_birth__lt=self.born_before)

        if self.donation_after is not None:
            q = q & Q(payments__created__gt=self.donation_after, **DONATION_FILTER)

        if self.donation_not_after is not None:
            q = q & ~Q(payments__created__gt=self.donation_not_after, **DONATION_FILTER)

        if self.donation_total_min or self.donation_total_max:
            donation_range = (
                {
                    "payments__created__gt": self.donation_total_range.lower,
                    "payments__created__lt": self.donation_total_range.upper,
                }
                if self.donation_total_range
                else {}
            )
            annotated_qs = Person.objects.annotate(
                donation_total=Sum(
                    "payments__price", filter=Q(**DONATION_FILTER, **donation_range)
                )
            )

            if self.donation_total_min:
                annotated_qs = annotated_qs.filter(
                    donation_total__gte=self.donation_total_min
                )

            if self.donation_total_max:
                annotated_qs = annotated_qs.filter(
                    donation_total__lte=self.donation_total_max
                )

            q = q & Q(id__in=annotated_qs.values_list("id"))

        if self.subscription is not None:
            if self.subscription:
                q = q & Q(subscriptions__status=Subscription.STATUS_ACTIVE)
            else:
                q = q & ~Q(subscriptions__status=Subscription.STATUS_ACTIVE)

        if self.add_segments.all().count() > 0:
            q = reduce(
                lambda q1, q2: q1 | q2,
                (s.get_subscribers_q() for s in self.add_segments.all()),
                q,
            )

        if self.exclude_segments.all().count() > 0:
            q = reduce(
                lambda q1, q2: q1 & ~q2,
                (s.get_subscribers_q() for s in self.exclude_segments.all()),
                q,
            )

        return q

    def get_subscribers_queryset(self):
        return (
            Person.objects.filter(self.get_subscribers_q())
            .order_by("id")
            .distinct("id")
        )

    def get_subscribers_count(self):
        return self.get_subscribers_queryset().count()

    get_subscribers_count.short_description = "Personnes"
    get_subscribers_count.help_text = "Estimation du nombre d'inscrits"

    def __str__(self):
        return self.name
