from django.contrib.gis.db.models import PolygonField
from django.db import models

from django.db.models import Q
from nuntius.models import BaseSegment

from agir.people.models import Person


class Segment(BaseSegment, models.Model):
    GA_STATUS_MEMBER = "m"
    GA_STATUS_MANAGER = "M"
    GA_STATUS_REFERENT = "R"
    GA_STATUS_CHOICES = (
        (GA_STATUS_MEMBER, "Membres de GA"),
        (GA_STATUS_MANAGER, "Animateurices et gestionnaires de GA"),
        (GA_STATUS_REFERENT, "Animateurices de GA"),
    )

    name = models.CharField("Nom", max_length=255)

    tags = models.ManyToManyField("people.PersonTag", blank=True)
    supportgroup_status = models.CharField(
        "Statut GA", max_length=1, choices=GA_STATUS_CHOICES, blank=True
    )
    supportgroup_subtypes = models.ManyToManyField(
        "groups.SupportGroupSubtype", verbose_name="Sous-types de groupes", blank=True
    )
    area = PolygonField("Territoire", blank=True, null=True)

    registration_date = models.DateTimeField(
        "Date d'inscription à la plateforme", blank=True, null=True
    )
    last_login = models.DateTimeField(
        "Date de dernière connexion à la plateforme", blank=True, null=True
    )

    def get_subscribers_queryset(self):
        qs = Person.objects.filter(
            subscribed=True, emails___bounced=False, emails___order=0
        )

        if self.tags.all().count() > 0:
            qs = qs.filter(tags__in=self.tags.all())

        if self.supportgroup_status:
            if self.supportgroup_status == self.GA_STATUS_MEMBER:
                query = Q(memberships__supportgroup__published=True)

            elif self.supportgroup_status == self.GA_STATUS_REFERENT:
                query = Q(
                    memberships__supportgroup__published=True,
                    memberships__is_referent=True,
                )
            elif self.supportgroup_status == self.GA_STATUS_MANAGER:
                query = Q(memberships__supportgroup__published=True) & (
                    Q(memberships__is_manager=True) | Q(memberships__is_referent=True)
                )

            if self.supportgroup_subtypes.all().count() > 0:
                query = query & Q(
                    memberships__supportgroup__subtypes__in=self.supportgroup_subtypes.all()
                )

            qs = qs.filter(query)

        if self.area is not None:
            qs = qs.filter(coordinates__coveredby=self.area)

        if self.registration_date is not None:
            qs = qs.filter(created__gt=self.registration_date)

        if self.last_login is not None:
            qs = qs.filter(role__last_login__gt=self.last_login)

        return qs.order_by("id").distinct("id")

    def get_subscribers_count(self):
        return self.get_subscribers_queryset().count()

    get_subscribers_count.short_description = "Personnes"
    get_subscribers_count.help_text = "Estimation du nombre d'inscrits"

    def __str__(self):
        return self.name
