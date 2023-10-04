from datetime import timedelta

from django.conf import settings
from django.contrib import admin
from django.contrib.humanize.templatetags import humanize
from django.db.models import Count, Q, OuterRef
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from agir.events.models import Event
from .. import models
from ..models import Membership
from ...lib.time import dehumanize_naturaltime


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


class CertificationWarningFilter(admin.SimpleListFilter):
    title = "avertissement de décertification"
    parameter_name = "certification_warning"
    WARNING_EXPIRATION_IN_DAYS = 31

    def lookups(self, request, model_admin):
        limit = humanize.apnumber(settings.CERTIFICATION_WARNING_EXPIRATION_IN_DAYS)
        return (
            ("sent", f"Envoyé"),
            ("expired", f"Envoyé depuis plus de {limit} jours"),
            (
                "unexpired",
                f"Envoyé depuis moins de {limit} jours",
            ),
        )

    def queryset(self, request, queryset):
        if self.value() == "sent":
            return queryset.with_certification_warning()

        if self.value() == "expired":
            return queryset.with_certification_warning(expired=True)

        if self.value() == "unexpired":
            return queryset.with_certification_warning(expired=False)

        return queryset


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


class LastManagerLoginFilter(admin.SimpleListFilter):
    title = "Dernière connexion d'un·e gestionnaire"
    parameter_name = "last_manager_login"

    def lookups(self, request, model_admin):
        return (
            ("1_week_ago", "Il y a plus d'une semaine"),
            ("1_month_ago", "Il y a plus d'un mois"),
            ("2_months_ago", "Il y a plus de deux mois"),
            ("3_months_ago", "Il y a plus de trois mois"),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        today = timezone.now().date()
        value = self.value().replace("_", " ")

        try:
            date = timezone.datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            try:
                date = dehumanize_naturaltime(value)
            except ValueError:
                return queryset

        if date is None or date.date() > today:
            return queryset

        date = date.date()

        qs = queryset.exclude(
            pk__in=(
                Membership.objects.filter(supportgroup_id=OuterRef("pk"))
                .managers()
                .active()
                .filter(person__role__last_login__date__gt=date)
                .values_list("supportgroup_id", flat=True)
            )
        )

        return qs
