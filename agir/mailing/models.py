from datetime import timedelta

from django.contrib.gis.db.models import MultiPolygonField
from django.contrib.postgres.fields import DateRangeField
from django.db import models
from django.db.models import Q, Sum
from django.utils.timezone import now
from django_countries.fields import CountryField
from nuntius.models import BaseSegment, CampaignSentStatusType

from agir.events.models import RSVP
from agir.groups.models import Membership
from agir.lib import data
from agir.lib.model_fields import ChoiceArrayField
from agir.payments.model_fields import AmountField
from agir.payments.models import Subscription, Payment
from agir.people.models import (
    Person,
    PersonQualification,
)

__all__ = ["Segment"]


DATE_HELP_TEXT = (
    "Écrivez en toute lettre JJ/MM/AAAA plutôt qu'avec le widget, ça ira plus vite."
)

DONATION_FILTER = {
    "payments__type__startswith": "don",
    "payments__status": Payment.STATUS_COMPLETED,
}


def default_newsletters():
    return [
        Person.NEWSLETTER_2022,
        Person.NEWSLETTER_2022_EXCEPTIONNEL,
    ]


class Segment(BaseSegment, models.Model):
    GA_STATUS_NOT_MEMBER = "N"
    GA_STATUS_MEMBER = "m"
    GA_STATUS_MANAGER = "M"
    GA_STATUS_REFERENT = "R"
    GA_STATUS_CHOICES = (
        (GA_STATUS_NOT_MEMBER, "Non membres de GA"),
        (GA_STATUS_MEMBER, "Membres de GA"),
        (GA_STATUS_MANAGER, "Animateur·ices et gestionnaires de GA"),
        (GA_STATUS_REFERENT, "Animateur·ices de GA"),
    )

    name = models.CharField("Nom", max_length=255)

    tags = models.ManyToManyField(
        "people.PersonTag",
        help_text="Limiter le segment aux personnes ayant les tags sélectionnés",
        blank=True,
    )
    excluded_tags = models.ManyToManyField(
        "people.PersonTag",
        verbose_name="Tags à exclure",
        help_text="Limite le segment aux personnes n'ayant pas les tags sélectionnés "
        "(l'exclusion d'un tag aura la précédence sur son inclusion)",
        related_name="+",
        blank=True,
    )

    qualifications = models.ManyToManyField(
        "people.Qualification",
        verbose_name="Type de statut",
        blank=True,
    )
    person_qualification_status = ChoiceArrayField(
        models.CharField(choices=PersonQualification.Status.choices, max_length=1),
        verbose_name="État du statut",
        help_text="Si un type de statut est indiqué, limiter aux personnes dont les statuts de ce type sont dans l'un des états choisis",
        default=list,
        blank=True,
        null=False,
    )

    is_2022 = models.BooleanField("Inscrits NSP", null=True, blank=True, default=True)
    is_insoumise = models.BooleanField(
        "Inscrits LFI",
        null=True,
        blank=True,
    )

    newsletters = ChoiceArrayField(
        models.CharField(choices=Person.NEWSLETTERS_CHOICES, max_length=255),
        default=default_newsletters,
        help_text="Inclure les personnes abonnées aux newsletters suivantes.",
        blank=True,
    )
    supportgroup_status = models.CharField(
        "Limiter aux membres de groupes ayant ce statut",
        max_length=1,
        choices=GA_STATUS_CHOICES,
        blank=True,
    )
    supportgroups = models.ManyToManyField(
        "groups.SupportGroup",
        verbose_name="Limiter aux membres d'un de ces groupes",
        blank=True,
    )
    supportgroup_subtypes = models.ManyToManyField(
        "groups.SupportGroupSubtype",
        verbose_name="Limiter aux membres de groupes d'un de ces sous-types",
        blank=True,
        help_text="Ce filtre ne sera pas appliqué lorsque le filtre "
        "'Limiter aux membres d'un de ces groupes' est actif",
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

    draw_status = models.BooleanField(
        "Limiter aux gens dont l'inscription au tirage au sort est",
        null=True,
        blank=True,
        default=None,
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

    last_open = models.IntegerField(
        "Limiter aux personnes ayant ouvert un email envoyé au court de derniers jours",
        help_text="Indiquer le nombre de jours",
        blank=True,
        null=True,
    )

    last_click = models.IntegerField(
        "Limiter aux personnes ayant cliqué dans un email envoyé au court des derniers jours",
        help_text="Indiquer le nombre de jours",
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

    registration_date_before = models.DateTimeField(
        "Limiter aux membres inscrit⋅e⋅s avant cette date", blank=True, null=True
    )

    registration_duration = models.IntegerField(
        "Limiter aux membres inscrit⋅e⋅s depuis au moins un certain nombre d'heures",
        help_text="Indiquer le nombre d'heures",
        blank=True,
        null=True,
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

    ELUS_NON = "N"
    ELUS_MEMBRE_RESEAU = "M"
    ELUS_REFERENCE = "R"
    ELUS_SAUF_EXCLUS = "E"
    ELUS_CHOICES = (
        ("", "Peu importe"),
        (ELUS_MEMBRE_RESEAU, "Uniquement les membres du réseau des élus"),
        (ELUS_SAUF_EXCLUS, "Tous les élus, sauf les exclus du réseau"),
        (
            ELUS_REFERENCE,
            "Les membres du réseau plus tout ceux à qui on a pas encore demandé",
        ),
    )

    elu = models.CharField("Est un élu", max_length=1, choices=ELUS_CHOICES, blank=True)

    elu_municipal = models.BooleanField("Avec un mandat municipal", default=True)
    elu_departemental = models.BooleanField(
        "Avec un mandat départemental", default=True
    )
    elu_regional = models.BooleanField("Avec un mandat régional", default=True)
    elu_consulaire = models.BooleanField("Avec un mandat consulaire", default=True)
    elu_depute = models.BooleanField("Avec un mandat de député", default=True)
    elu_depute_europeen = models.BooleanField(
        "avec un mandat de député européen", default=True
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

    def apply_supportgroup_filters(self, query):
        supportgroup_ids = self.supportgroups.values_list("id", flat=True)
        subtype_ids = self.supportgroup_subtypes.values_list("id", flat=True)

        if (
            not self.supportgroup_status
            and len(subtype_ids) == 0
            and len(supportgroup_ids) == 0
        ):
            return query

        # Simplify queries for supportgroup_status only filtering
        if len(subtype_ids) == 0 and len(supportgroup_ids) == 0:
            if self.supportgroup_status == self.GA_STATUS_NOT_MEMBER:
                return query & ~Q(memberships__supportgroup__published=True)
            if self.supportgroup_status == self.GA_STATUS_MEMBER:
                return query & Q(memberships__supportgroup__published=True)
            if self.supportgroup_status == self.GA_STATUS_REFERENT:
                return query & Q(
                    memberships__supportgroup__published=True,
                    memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
                )
            if self.supportgroup_status == self.GA_STATUS_MANAGER:
                return query & Q(
                    memberships__supportgroup__published=True,
                    memberships__membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
                )

        # Use membership subquery for multi-field supportgroup filtering
        memberships = Membership.objects.filter(supportgroup__published=True)

        if len(supportgroup_ids) > 0:
            memberships = memberships.filter(supportgroup_id__in=supportgroup_ids)
        elif len(subtype_ids) > 0:
            memberships = memberships.filter(supportgroup__subtypes__id__in=subtype_ids)

        if self.supportgroup_status == self.GA_STATUS_REFERENT:
            memberships = memberships.filter(
                membership_type__gte=Membership.MEMBERSHIP_TYPE_REFERENT,
            )
        if self.supportgroup_status == self.GA_STATUS_MANAGER:
            memberships = memberships.filter(
                membership_type__gte=Membership.MEMBERSHIP_TYPE_MANAGER,
            )

        member_ids = (
            memberships.distinct("person_id")
            .order_by("person_id")
            .values_list("person_id", flat=True)
        )

        if self.supportgroup_status == self.GA_STATUS_NOT_MEMBER:
            return query & ~Q(id__in=member_ids)

        return query & Q(id__in=member_ids)

    def apply_qualification_filters(self, query):
        qualification_ids = list(self.qualifications.values_list("pk", flat=True))

        if not qualification_ids:
            return query

        person_qualifications = PersonQualification.objects.filter(
            qualification_id__in=qualification_ids
        )

        if self.person_qualification_status:
            person_qualifications = person_qualifications.only_statuses(
                statuses=self.person_qualification_status
            )

        return query & Q(
            id__in=person_qualifications.values_list("person_id", flat=True)
        )

    def apply_tag_filters(self, query):
        excluded_tags = list(self.excluded_tags.values_list("pk", flat=True))
        if len(excluded_tags) > 0:
            query &= ~Q(tags__pk__in=excluded_tags)

        tags = list(self.tags.values_list("pk", flat=True))
        if len(tags) > 0:
            query &= Q(tags__pk__in=tags)

        return query

    def get_subscribers_q(self):
        # ne pas inclure les rôles inactifs dans les envois de mail
        q = ~Q(role__is_active=False)

        # permettre de créer des segments capables d'inclure des personnes inscrites à aucune des newsletters
        if self.newsletters:
            q &= Q(newsletters__overlap=self.newsletters)

        if self.is_insoumise is not None:
            q = q & Q(is_insoumise=self.is_insoumise)

        if self.is_2022 is not None:
            q = q & Q(is_2022=self.is_2022)

        q = self.apply_tag_filters(q)

        q = self.apply_qualification_filters(q)

        q = self.apply_supportgroup_filters(q)

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

        if self.draw_status is not None:
            q = q & Q(draw_participation=self.draw_status)

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
                campaignsentevent__datetime__gt=now() - timedelta(days=self.last_open),
            )

        if self.last_click is not None:
            q = q & Q(
                campaignsentevent__click_count__gt=0,
                campaignsentevent__datetime__gt=now() - timedelta(days=self.last_click),
            )

        if len(self.countries) > 0:
            q = q & Q(location_country__in=self.countries)

        if len(self.departements) > 0:
            q = q & Q(data.filtre_departements(*self.departements))

        if self.area is not None:
            q = q & Q(coordinates__intersects=self.area)

        if self.registration_date is not None:
            q = q & Q(created__gt=self.registration_date)

        if self.registration_date_before is not None:
            q = q & Q(created__lt=self.registration_date_before)

        if self.registration_duration:
            q = q & Q(created__lt=now() - timedelta(hours=self.registration_duration))

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

        if self.elu:
            if self.elu == Segment.ELUS_MEMBRE_RESEAU:
                q &= Q(membre_reseau_elus=Person.MEMBRE_RESEAU_OUI)
            elif self.elu == Segment.ELUS_SAUF_EXCLUS:
                q &= ~Q(membre_reseau_elus=Person.MEMBRE_RESEAU_EXCLUS)
            elif self.elu == Segment.ELUS_REFERENCE:
                q &= ~Q(
                    membre_reseau_elus__in=[
                        Person.MEMBRE_RESEAU_EXCLUS,
                        Person.MEMBRE_RESEAU_NON,
                    ]
                )

            q_mandats = Q()
            for t in [
                "elu_municipal",
                "elu_departemental",
                "elu_regional",
                "elu_consulaire",
                "elu_depute",
                "elu_depute_europeen",
            ]:
                if getattr(self, t):
                    q_mandats |= Q(**{t: True})
            q &= q_mandats

        return q

    def _get_own_filters_queryset(self):
        qs = Person.objects.all()

        if self.elu:
            qs = qs.annotate_elus()

        return qs.filter(self.get_subscribers_q()).filter(emails___bounced=False)

    def get_subscribers_queryset(self):
        qs = self._get_own_filters_queryset()

        for s in self.add_segments.all():
            qs = Person.objects.filter(
                Q(pk__in=qs) | Q(pk__in=s.get_subscribers_queryset())
            )

        for s in self.exclude_segments.all():
            qs = qs.exclude(pk__in=s.get_subscribers_queryset())

        return qs.order_by("id", "emails___order").distinct("id")

    def get_subscribers_count(self):
        return (
            self._get_own_filters_queryset().order_by("id").distinct("id").count()
            + sum(s.get_subscribers_count() for s in self.add_segments.all())
            - sum(s.get_subscribers_count() for s in self.exclude_segments.all())
        )

    def is_subscriber(self, person):
        qs = Person.objects.filter(pk=person.pk)
        if self.elu:
            qs = qs.annotate_elus()

        qs = qs.filter(self.get_subscribers_q())
        is_subscriber = qs.exists()

        if not is_subscriber:
            for segment in self.add_segments.all():
                if segment.is_subscriber(person):
                    is_subscriber = True
                    break

        if is_subscriber:
            for segment in self.exclude_segments.all():
                if segment.is_subscriber(person):
                    is_subscriber = False
                    break

        return is_subscriber

    get_subscribers_count.short_description = "Personnes"
    get_subscribers_count.help_text = "Estimation du nombre d'inscrits"

    def __str__(self):
        return self.name
