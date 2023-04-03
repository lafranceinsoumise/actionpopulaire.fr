from datetime import timedelta

from django.contrib import admin
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from agir.events.models import Event
from .. import models
from ..models import Membership


class GroupHasEventsFilter(admin.SimpleListFilter):
    title = _("Événements organisés dans les 2 mois précédents ou mois à venir")

    parameter_name = "is_active"

    def lookups(self, request, model_admin):
        return (("yes", _("Oui")), ("no", _("Non")))

    def queryset(self, request, queryset):
        queryset = queryset.annotate(
            current_events_count=Count(
                "organized_events",
                filter=Q(
                    organized_events__start_time__range=(
                        timezone.now() - timedelta(days=62),
                        timezone.now() + timedelta(days=31),
                    ),
                    organized_events__visibility=Event.VISIBILITY_PUBLIC,
                ),
            )
        )
        if self.value() == "yes":
            return queryset.exclude(current_events_count=0)
        if self.value() == "no":
            return queryset.filter(current_events_count=0)


class CertifiedSupportGroupFilter(admin.SimpleListFilter):
    title = "certification"
    parameter_name = "certified"

    def lookups(self, request, model_admin):
        return ("yes", _("Groupe certifiés")), ("no", _("Groupes non certifiés"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.certified()
        if self.value() == "no":
            return queryset.uncertified()


class MembersFilter(admin.SimpleListFilter):
    title = "Membres"
    parameter_name = "members"

    def lookups(self, request, model_admin):
        return (("no_members", "Aucun membre"), ("no_referent", "Aucun animateur"))

    def queryset(self, request, queryset):
        if self.value() == "no_members":
            return queryset.filter(members=None)

        if self.value() == "no_referent":
            return queryset.exclude(
                memberships__membership_type=Membership.MEMBERSHIP_TYPE_REFERENT
            )


class TooMuchMembersFilter(admin.SimpleListFilter):
    MEMBERS_LIMIT = models.SupportGroup.MEMBERSHIP_LIMIT

    title = "Groupe d'action avec trop de membres ({} actuellement)".format(
        MEMBERS_LIMIT
    )
    parameter_name = "group with too much members"

    def lookups(self, request, model_admin):
        return (
            (
                "less_than_{}_members".format(self.MEMBERS_LIMIT),
                "Moins de {} membres".format(self.MEMBERS_LIMIT),
            ),
            (
                "more_than_{}_members".format(self.MEMBERS_LIMIT),
                "Plus de {} membres".format(self.MEMBERS_LIMIT),
            ),
        )

    def queryset(self, request, queryset):
        if self.value() == "less_than_{}_members".format(self.MEMBERS_LIMIT):
            return queryset.filter(membership_count__lt=self.MEMBERS_LIMIT)
        if self.value() == "more_than_{}_members".format(self.MEMBERS_LIMIT):
            return queryset.filter(membership_count__gte=self.MEMBERS_LIMIT)
