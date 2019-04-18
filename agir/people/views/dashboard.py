from datetime import timedelta

from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Value, F, TextField, Q, Count, Case, When, BooleanField
from django.utils import timezone
from django.views.generic import TemplateView

from agir.authentication.view_mixins import SoftLoginRequiredMixin
from agir.events.models import Event
from agir.groups.actions import get_next_promo_code
from agir.groups.actions.promo_codes import is_promo_code_delayed, next_promo_code_date
from agir.groups.models import SupportGroup
from agir.events.views.utils import group_events_by_day
from agir.lib.tasks import geocode_person


class DashboardView(SoftLoginRequiredMixin, TemplateView):
    template_name = "people/dashboard.html"

    def get(self, request, *args, **kwargs):
        person = request.user.person

        if person.coordinates_type is None:
            geocode_person.delay(person.pk)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        person = self.request.user.person

        rsvped_events = (
            Event.objects.upcoming()
            .filter(attendees=person)
            .order_by("start_time", "end_time")
        )
        if person.coordinates is not None:
            rsvped_events = rsvped_events.annotate(
                distance=Distance("coordinates", person.coordinates)
            )
        members_groups = list(
            SupportGroup.objects.filter(memberships__person=person, published=True)
            .order_by("name")
            .annotate(
                user_is_manager=F("memberships__is_manager")._combine(
                    F("memberships__is_referent"), "OR", False
                ),
                has_promo_code=Count(
                    Case(
                        When(tags__label=settings.PROMO_CODE_TAG, then=1),
                        default=0,
                        output_field=BooleanField(),
                    )
                ),
            )
        )

        if is_promo_code_delayed():
            promo_code_delay = next_promo_code_date()
        else:
            for group in members_groups:
                if group.user_is_manager and group.has_promo_code:
                    group.promo_code = get_next_promo_code(group)
            promo_code_delay = None

        suggested_events = (
            Event.objects.upcoming()
            .exclude(rsvps__person=person)
            .filter(organizers_groups__in=person.supportgroups.all())
            .annotate(
                reason=Value(
                    "Cet événément est organisé par un groupe dont vous êtes membre.",
                    TextField(),
                )
            )
            .order_by("start_time")
        )
        if person.coordinates is not None:
            suggested_events = suggested_events.annotate(
                distance=Distance("coordinates", person.coordinates)
            )

        last_events = (
            Event.objects.past()
            .filter(Q(attendees=person) | Q())
            .order_by("-start_time", "-end_time")[:10]
        )

        if person.coordinates is not None and len(suggested_events) < 10:
            close_events = (
                Event.objects.upcoming()
                .filter(start_time__lt=timezone.now() + timedelta(days=30))
                .exclude(pk__in=suggested_events)
                .exclude(rsvps__person=person)
                .annotate(
                    reason=Value(
                        "Cet événement se déroule près de chez vous.", TextField()
                    )
                )
                .annotate(distance=Distance("coordinates", person.coordinates))
                .order_by("distance")[: (10 - suggested_events.count())]
            )

            suggested_events = close_events.union(suggested_events).order_by(
                "start_time"
            )

        organized_events = (
            Event.objects.upcoming(published_only=False)
            .filter(organizers=person)
            .exclude(visibility=Event.VISIBILITY_ADMIN)
            .order_by("start_time")
        )
        past_organized_events = (
            Event.objects.past()
            .filter(organizers=person)
            .order_by("-start_time", "-end_time")[:10]
        )

        past_reports = (
            Event.objects.past()
            .exclude(rsvps__person=person)
            .exclude(report_content="")
            .filter(start_time__gt=timezone.now() - timedelta(days=30))
            .order_by("-start_time")
        )
        if person.coordinates is not None:
            past_reports = past_reports.annotate(
                distance=Distance("coordinates", person.coordinates)
            ).order_by("distance")[:5]

        kwargs.update(
            {
                "person": person,
                "rsvped_events": group_events_by_day(rsvped_events),
                "members_groups": members_groups,
                "promo_code_delay": promo_code_delay,
                "suggested_events": group_events_by_day(suggested_events),
                "last_events": last_events,
                "past_reports": past_reports,
                "organized_events": organized_events,
                "past_organized_events": past_organized_events,
            }
        )
        return super().get_context_data(**kwargs)
