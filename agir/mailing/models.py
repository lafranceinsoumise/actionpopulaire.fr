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
    support_group_status = models.CharField(
        "Statut GA", max_length=1, choices=GA_STATUS_CHOICES, blank=True
    )
    area = PolygonField("Territoire", blank=True, null=True)

    def get_subscribers_queryset(self):
        qs = Person.objects.filter(
            subscribed=True, emails___bounced=False, emails___order=0
        )

        if self.tags.all().count() > 0:
            qs = qs.filter(tags__in=self.tags.all())

        if self.support_group_status == self.GA_STATUS_REFERENT:
            qs = qs.filter(
                membership__supportgroup__published=True, membership__is_referent=True
            )
        if self.support_group_status == self.GA_STATUS_MANAGER:
            qs = qs.filter(
                Q(membership__supportgroup__published=True)
                & Q(membership__is_manager=True)
                | Q(membership__is_referent=True)
            )
        if self.support_group_status == self.GA_STATUS_MEMBER:
            qs = qs.filter(supportgroups__published=True)

        if self.area is not None:
            qs = qs.filter(coordinates__coveredby=self.area)

        return qs.order_by("id").distinct("id")

    def get_subscribers_count(self):
        return self.get_subscribers_queryset().count()

    get_subscribers_count.short_description = "Personnes"
    get_subscribers_count.help_text = "Estimation du nombre d'inscrits"

    def __str__(self):
        return self.name
